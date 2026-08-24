from pathlib import Path
from urllib.parse import parse_qs

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="پاک‌سازی ایمن ریپو",
    description="پیش‌نمایش دامنه حذف بدون انجام عملیات مخرب.",
    version="1.0.0",
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


class CleanupRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    delete_working_files: bool = Field(
        default=False,
        description="حذف فایل‌ها و پوشه‌های کاری معمولی",
    )
    delete_hidden_files: bool = Field(
        default=False,
        description="حذف فایل‌های مخفی و تنظیمات مانند CI و gitignore",
    )
    preserve_git_metadata: bool = Field(
        default=True,
        description="حفظ پوشه متادیتای Git",
    )
    preserve_app_skeleton: bool = Field(
        default=True,
        description="حفظ اسکلت قابل اجرای FastAPI",
    )
    explicit_confirmation: bool = Field(
        default=False,
        description="تأیید صریح دامنه عملیات",
    )


class CleanupPreview(BaseModel):
    status: str
    message: str
    included: list[str]
    preserved: list[str]
    destructive_action_performed: bool


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    del request
    html = (BASE_DIR / "static" / "index.html").read_text(encoding="utf-8")
    return HTMLResponse(html)


@app.post("/api/preview", response_model=CleanupPreview)
def preview(payload: CleanupRequest) -> CleanupPreview:
    if not payload.explicit_confirmation:
        return CleanupPreview(
            status="confirmation_required",
            message="برای بررسی دامنه، تأیید صریح گزینه‌های انتخاب‌شده لازم است.",
            included=[],
            preserved=[".git (به‌صورت پیش‌فرض)", "اسکلت اپلیکیشن (به‌صورت پیش‌فرض)"],
            destructive_action_performed=False,
        )

    included: list[str] = []
    preserved: list[str] = []

    if payload.delete_working_files:
        included.append("فایل‌ها و پوشه‌های کاری معمولی")
    else:
        preserved.append("فایل‌ها و پوشه‌های کاری معمولی")

    if payload.delete_hidden_files:
        included.append("فایل‌های مخفی، تنظیمات و CI/CD")
    else:
        preserved.append("فایل‌های مخفی، تنظیمات و CI/CD")

    if payload.preserve_git_metadata:
        preserved.append("متادیتای Git مانند .git")
    else:
        included.append("متادیتای Git مانند .git")

    if payload.preserve_app_skeleton:
        preserved.append("اسکلت FastAPI و رابط vanilla")
    else:
        included.append("اسکلت FastAPI و رابط vanilla")

    return CleanupPreview(
        status="preview_only",
        message="دامنه انتخاب‌شده ثبت شد؛ هیچ فایل یا پوشه‌ای در این نسخه حذف نشده است.",
        included=included,
        preserved=preserved,
        destructive_action_performed=False,
    )


def _form_boolean(values: dict[str, list[str]], name: str, default: bool = False) -> bool:
    """Convert an HTML form checkbox value to bool without requiring multipart."""
    if name not in values:
        return default
    value = values[name][-1].strip().lower()
    return value in {"1", "true", "on", "yes"}


@app.post("/api/form-preview", response_model=CleanupPreview)
async def form_preview(request: Request) -> CleanupPreview:
    """Create the same non-destructive preview from a URL-encoded HTML form.

    Parsing the request body locally avoids FastAPI's optional multipart dependency.
    The browser form uses URL encoding, and no filesystem operation is performed.
    """
    raw_body = await request.body()
    values = parse_qs(raw_body.decode("utf-8"), keep_blank_values=True)
    return preview(
        CleanupRequest(
            delete_working_files=_form_boolean(values, "delete_working_files"),
            delete_hidden_files=_form_boolean(values, "delete_hidden_files"),
            preserve_git_metadata=_form_boolean(
                values, "preserve_git_metadata", default=True
            ),
            preserve_app_skeleton=_form_boolean(
                values, "preserve_app_skeleton", default=True
            ),
            explicit_confirmation=_form_boolean(values, "explicit_confirmation"),
        )
    )
