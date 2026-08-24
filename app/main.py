from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class OperationStatus(BaseModel):
    scope: str
    operation_state: str
    confirmation_required: bool
    deletion_performed: bool
    scope_rules: list[str]
    pre_operation_inventory: list[str]
    deleted_items: list[str]
    remaining_items: list[str]
    preserved_items: list[str]
    out_of_scope: list[str]
    reason: str
    checked_at: str


def project_inventory() -> list[str]:
    """Return every entry below PROJECT_ROOT, without following links outside it."""
    entries: list[str] = []
    for path in PROJECT_ROOT.rglob("*"):
        try:
            relative = path.relative_to(PROJECT_ROOT).as_posix()
        except ValueError:
            # Defensive guard: an entry outside the approved root is never reported.
            continue
        if path.is_dir() and not path.is_symlink():
            relative += "/"
        entries.append(relative)
    return sorted(entries)


app = FastAPI(
    title="گزارش عملیات حذف فایل‌ها",
    version="1.1.0",
    description="گزارش واقعی inventory با توقف حذف تا دریافت تأیید صریح.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/status", response_model=OperationStatus)
def operation_status() -> OperationStatus:
    # This is intentionally a no-op. The approved plan requires human confirmation
    # of the path scope and exceptions before any destructive operation.
    inventory = project_inventory()
    return OperationStatus(
        scope="ریشهٔ پروژه (فقط موارد زیر این مسیر)",
        operation_state="در انتظار تأیید دامنه و استثناها",
        confirmation_required=True,
        deletion_performed=False,
        scope_rules=[
            "دامنه فقط ریشهٔ پروژه و تمام فایل‌ها و پوشه‌های زیر آن است.",
            "فایل‌های مخفی نیز در inventory ریشهٔ پروژه شمرده می‌شوند.",
            "پوشه‌های وابستگی و فایل‌های تولیدشده، اگر زیر ریشه باشند، شمرده می‌شوند؛ حذف نمی‌شوند.",
            "مسیرهای خارج از ریشهٔ پروژه هرگز مشمول عملیات یا inventory نیستند.",
            "app/main.py و app/__init__.py برای حفظ app.main:app مستثنا هستند.",
        ],
        pre_operation_inventory=inventory,
        deleted_items=[],
        remaining_items=inventory,
        preserved_items=inventory,
        out_of_scope=["تمام مسیرهای خارج از ریشهٔ پروژه"],
        reason=(
            "هیچ فایل یا پوشه‌ای حذف یا تغییر داده نشده است؛ دامنه، شمول فایل‌های مخفی، "
            "وابستگی‌ها و تولیدشده‌ها و استثناهای لازم برای app.main:app هنوز تأیید انسانی نشده‌اند."
        ),
        checked_at=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return """
<!doctype html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>گزارش حذف فایل‌ها</title>
  <style>
    :root { color-scheme: light; font-family: Tahoma, sans-serif; }
    body { margin: 0; background: #f4f6f8; color: #17202a; }
    main { max-width: 860px; margin: 4rem auto; padding: 0 1rem; }
    .card { background: white; border-radius: 16px; padding: 2rem; box-shadow: 0 8px 30px #17202a18; }
    h1 { margin-top: 0; color: #173b57; }
    .notice { border-right: 5px solid #e09f3e; background: #fff7e8; padding: 1rem; line-height: 1.9; }
    dl { display: grid; grid-template-columns: 180px 1fr; gap: .75rem 1rem; line-height: 1.8; }
    dt { font-weight: bold; color: #52616b; }
    dd { margin: 0; }
    button { border: 0; border-radius: 8px; padding: .75rem 1rem; background: #176b87; color: white; cursor: pointer; font-size: 1rem; }
    button:hover { background: #12546a; }
    pre { direction: ltr; text-align: left; white-space: pre-wrap; background: #eef2f5; padding: 1rem; border-radius: 8px; max-height: 22rem; overflow: auto; }
    .ok { color: #18794e; font-weight: bold; }
  </style>
</head>
<body>
<main><section class="card">
  <h1>گزارش عملیات حذف فایل‌ها</h1>
  <p class="notice">تا زمانی که دامنه و استثناها صریحاً تأیید نشوند، هیچ حذف فیزیکی انجام نمی‌شود. inventory زیر فقط به ریشهٔ پروژه محدود است و <code>app.main:app</code> باید حفظ شود.</p>
  <dl>
    <dt>وضعیت</dt><dd id="state" class="ok">در حال دریافت...</dd>
    <dt>محدودهٔ بررسی</dt><dd id="scope">در حال دریافت...</dd>
    <dt>پیش از عملیات</dt><dd id="before">در حال دریافت...</dd>
    <dt>حذف‌شده</dt><dd id="deleted">در حال دریافت...</dd>
    <dt>باقی‌مانده</dt><dd id="remaining">در حال دریافت...</dd>
    <dt>سیاست دامنه</dt><dd><ul id="rules"></ul></dd>
    <dt>دلیل</dt><dd id="reason">در حال دریافت...</dd>
  </dl>
  <button id="refresh" type="button">به‌روزرسانی گزارش</button>
  <pre id="error" hidden></pre>
</section></main>
<script>
  async function loadStatus() {
    const error = document.getElementById('error'); error.hidden = true;
    try {
      const response = await fetch('/api/status');
      if (!response.ok) throw new Error('HTTP ' + response.status);
      const data = await response.json();
      document.getElementById('state').textContent = data.operation_state;
      document.getElementById('scope').textContent = data.scope;
      document.getElementById('before').textContent = data.pre_operation_inventory.length + ' مورد';
      document.getElementById('deleted').textContent = data.deleted_items.length ? data.deleted_items.join('، ') : 'هیچ موردی';
      document.getElementById('remaining').textContent = data.remaining_items.length + ' مورد';
      document.getElementById('reason').textContent = data.reason;
      document.getElementById('rules').replaceChildren(...data.scope_rules.map(rule => { const li = document.createElement('li'); li.textContent = rule; return li; }));
    } catch (exc) { error.hidden = false; error.textContent = 'دریافت گزارش ناموفق بود: ' + exc.message; }
  }
  document.getElementById('refresh').addEventListener('click', loadStatus); loadStatus();
</script>
</body></html>
"""
