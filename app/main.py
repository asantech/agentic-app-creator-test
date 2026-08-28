from typing import Any

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, validator

app = FastAPI(title="فرم درخواست وام")


class LoanApplication(BaseModel):
    full_name: str = Field(..., min_length=1)
    age: float = Field(..., ge=0)
    score: float = Field(..., ge=0)
    requested_loan: float = Field(..., ge=0)
    salary: float = Field(..., ge=0)
    salary_deduction: float = Field(..., ge=0)
    collateral: float = Field(..., ge=0)
    occupation: str = Field(..., min_length=1)
    work_years: float = Field(..., ge=0)

    @validator("full_name", "occupation")
    def text_must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("مقدار متنی نمی‌تواند خالی باشد")
        return cleaned


PAGE = """<!doctype html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>درخواست وام</title>
  <style>
    :root { font-family: Tahoma, Arial, sans-serif; color: #172033; background: #eef3f8; }
    * { box-sizing: border-box; }
    body { margin: 0; min-height: 100vh; display: grid; place-items: center; padding: 24px; }
    main { width: min(760px, 100%); background: #fff; border-radius: 18px; padding: 30px; box-shadow: 0 12px 32px #20334a1c; }
    h1 { margin: 0 0 8px; color: #1d4d7a; font-size: 2rem; }
    .intro { margin: 0 0 24px; color: #5e6b7b; }
    .fields { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; }
    label { display: flex; flex-direction: column; gap: 7px; font-weight: 700; }
    input { border: 1px solid #cbd5e1; border-radius: 9px; padding: 11px 12px; font: inherit; color: inherit; }
    input:focus { outline: 3px solid #93c5fd; border-color: #2563eb; }
    .actions { margin-top: 24px; display: flex; align-items: center; gap: 16px; }
    button { border: 0; border-radius: 9px; padding: 12px 30px; background: #1769aa; color: #fff; font: inherit; font-weight: 700; cursor: pointer; }
    button:hover { background: #12558a; }
    button:disabled { opacity: .65; cursor: wait; }
    #result { min-height: 1.5em; font-weight: 700; }
    .success { color: #137333; }
    .error { color: #b42318; }
    @media (max-width: 600px) { .fields { grid-template-columns: 1fr; } main { padding: 22px; } }
  </style>
</head>
<body>
  <main>
    <h1>درخواست وام</h1>
    <p class="intro">لطفاً اطلاعات خود را برای بررسی درخواست وارد کنید.</p>
    <form id="loan-form">
      <div class="fields">
        <label for="full_name">نام و نام خانوادگی
          <input id="full_name" name="full_name" type="text" required>
        </label>
        <label for="age">سن
          <input id="age" name="age" type="number" min="0" step="any" required>
        </label>
        <label for="score">امتیاز
          <input id="score" name="score" type="number" min="0" step="any" required>
        </label>
        <label for="requested_loan">میزان وام درخواستی
          <input id="requested_loan" name="requested_loan" type="number" min="0" step="any" required>
        </label>
        <label for="salary">حقوق
          <input id="salary" name="salary" type="number" min="0" step="any" required>
        </label>
        <label for="salary_deduction">کسر از حقوق
          <input id="salary_deduction" name="salary_deduction" type="number" min="0" step="any" required>
        </label>
        <label for="collateral">مقدار وثیقه
          <input id="collateral" name="collateral" type="number" min="0" step="any" required>
        </label>
        <label for="occupation">شغل
          <input id="occupation" name="occupation" type="text" required>
        </label>
        <label for="work_years">سنوات کاری
          <input id="work_years" name="work_years" type="number" min="0" step="any" required>
        </label>
      </div>
      <div class="actions">
        <button id="submit-button" type="submit">تأیید</button>
        <p id="result" role="status" aria-live="polite"></p>
      </div>
    </form>
  </main>
  <script>
    const form = document.getElementById('loan-form');
    const result = document.getElementById('result');
    const button = document.getElementById('submit-button');
    const numericFields = ['age', 'score', 'requested_loan', 'salary', 'salary_deduction', 'collateral', 'work_years'];

    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const data = Object.fromEntries(new FormData(form).entries());
      numericFields.forEach((field) => { data[field] = Number(data[field]); });
      result.textContent = 'در حال بررسی...';
      result.className = '';
      button.disabled = true;
      try {
        const response = await fetch('/api/loan-applications', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        });
        const payload = await response.json();
        if (!response.ok) throw new Error(payload.detail ? 'لطفاً اطلاعات واردشده را بررسی کنید.' : 'خطا در ارسال اطلاعات');
        result.textContent = payload.message;
        result.className = 'success';
      } catch (error) {
        result.textContent = error.message || 'خطایی رخ داد.';
        result.className = 'error';
      } finally {
        button.disabled = false;
      }
    });
  </script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return PAGE


@app.post("/api/loan-applications")
def submit_loan_application(application: LoanApplication) -> dict[str, Any]:
    return {
        "success": True,
        "message": "درخواست وام با موفقیت دریافت و برای بررسی ثبت شد.",
        "application": application.model_dump() if hasattr(application, "model_dump") else application.dict(),
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
