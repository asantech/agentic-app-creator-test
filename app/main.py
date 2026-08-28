from typing import Annotated

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, validator

app = FastAPI(title="فرم درخواست وام")


class LoanRequest(BaseModel):
    full_name: str = Field(..., min_length=1)
    age: Annotated[float, Field(ge=0)]
    score: Annotated[float, Field(ge=0)]
    requested_loan: Annotated[float, Field(ge=0)]
    salary: Annotated[float, Field(ge=0)]
    salary_deduction: Annotated[float, Field(ge=0)]
    collateral: Annotated[float, Field(ge=0)]
    job: str = Field(..., min_length=1)
    work_years: Annotated[float, Field(ge=0)]

    @validator("full_name", "job")
    def text_must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("این مقدار نمی‌تواند خالی باشد")
        return cleaned


HTML_PAGE = """<!doctype html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>درخواست وام</title>
  <style>
    :root { color-scheme: light; font-family: Tahoma, Arial, sans-serif; }
    * { box-sizing: border-box; }
    body { margin: 0; min-height: 100vh; background: #eef3f8; color: #172b4d; }
    main { width: min(760px, calc(100% - 32px)); margin: 42px auto; }
    .card { background: #fff; border-radius: 18px; padding: 30px; box-shadow: 0 8px 30px #193b5918; }
    h1 { text-align: center; margin: 0 0 26px; color: #145da0; font-size: 2rem; }
    form { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; }
    .field { display: flex; flex-direction: column; gap: 7px; }
    label { font-weight: bold; font-size: .95rem; }
    input { border: 1px solid #bdc9d6; border-radius: 9px; padding: 11px 12px; font: inherit; direction: rtl; }
    input:focus { outline: 3px solid #b9dcf7; border-color: #2383c4; }
    .full { grid-column: 1 / -1; }
    button { grid-column: 1 / -1; border: 0; border-radius: 9px; padding: 13px; background: #1677b8; color: white; font: inherit; font-weight: bold; cursor: pointer; }
    button:hover { background: #105d91; }
    button:disabled { opacity: .65; cursor: wait; }
    #message { min-height: 24px; margin: 20px 0 0; text-align: center; font-weight: bold; }
    .success { color: #18734b; } .error { color: #b42318; }
    @media (max-width: 580px) { main { margin: 20px auto; } .card { padding: 20px; } form { grid-template-columns: 1fr; } .full { grid-column: auto; } button { grid-column: auto; } }
  </style>
</head>
<body>
  <main>
    <section class="card" aria-labelledby="page-title">
      <h1 id="page-title">درخواست وام</h1>
      <form id="loan-form" novalidate>
        <div class="field full"><label for="full_name">نام و نام خانوادگی</label><input id="full_name" name="full_name" type="text" required></div>
        <div class="field"><label for="age">سن</label><input id="age" name="age" type="number" min="0" step="any" required></div>
        <div class="field"><label for="score">امتیاز</label><input id="score" name="score" type="number" min="0" step="any" required></div>
        <div class="field"><label for="requested_loan">میزان وام درخواستی</label><input id="requested_loan" name="requested_loan" type="number" min="0" step="any" required></div>
        <div class="field"><label for="salary">حقوق</label><input id="salary" name="salary" type="number" min="0" step="any" required></div>
        <div class="field"><label for="salary_deduction">کسر از حقوق</label><input id="salary_deduction" name="salary_deduction" type="number" min="0" step="any" required></div>
        <div class="field"><label for="collateral">مقدار وثیقه</label><input id="collateral" name="collateral" type="number" min="0" step="any" required></div>
        <div class="field"><label for="job">شغل</label><input id="job" name="job" type="text" required></div>
        <div class="field"><label for="work_years">سنوات کاری</label><input id="work_years" name="work_years" type="number" min="0" step="any" required></div>
        <button id="submit-button" type="submit">تایید</button>
      </form>
      <p id="message" role="status" aria-live="polite"></p>
    </section>
  </main>
  <script>
    const form = document.getElementById('loan-form');
    const button = document.getElementById('submit-button');
    const message = document.getElementById('message');
    const numericFields = ['age', 'score', 'requested_loan', 'salary', 'salary_deduction', 'collateral', 'work_years'];

    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      message.textContent = '';
      message.className = '';
      const formData = new FormData(form);
      const data = Object.fromEntries(formData.entries());
      if (!data.full_name.trim() || !data.job.trim() || numericFields.some((name) => data[name] === '')) {
        message.textContent = 'لطفاً همهٔ فیلدها را کامل کنید.';
        message.className = 'error';
        return;
      }
      if (numericFields.some((name) => Number(data[name]) < 0 || Number.isNaN(Number(data[name])))) {
        message.textContent = 'مقادیر عددی نمی‌توانند منفی یا نامعتبر باشند.';
        message.className = 'error';
        return;
      }
      numericFields.forEach((name) => { data[name] = Number(data[name]); });
      button.disabled = true;
      button.textContent = 'در حال ارسال...';
      try {
        const response = await fetch('/api/loan-requests', {
          method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data)
        });
        const result = await response.json();
        if (!response.ok) throw new Error('اطلاعات واردشده معتبر نیست.');
        message.textContent = result.message || 'درخواست شما با موفقیت ثبت شد.';
        message.className = 'success';
        form.reset();
      } catch (error) {
        message.textContent = error.message || 'ارسال درخواست با خطا روبه‌رو شد.';
        message.className = 'error';
      } finally {
        button.disabled = false;
        button.textContent = 'تایید';
      }
    });
  </script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def home() -> HTMLResponse:
    return HTMLResponse(content=HTML_PAGE)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/loan-requests")
def submit_loan_request(request: LoanRequest) -> dict[str, str]:
    return {"message": "درخواست وام شما با موفقیت دریافت شد."}
