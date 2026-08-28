from typing import Annotated

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="فرم درخواست وام")


class LoanRequest(BaseModel):
    full_name: str = Field(min_length=1)
    age: Annotated[int, Field(ge=0)]
    score: Annotated[float, Field(ge=0)]
    requested_loan: Annotated[float, Field(ge=0)]
    salary: Annotated[float, Field(ge=0)]
    salary_deduction: Annotated[float, Field(ge=0)]
    collateral: Annotated[float, Field(ge=0)]
    occupation: str = Field(min_length=1)
    work_experience: Annotated[float, Field(ge=0)]

    @field_validator("full_name", "occupation")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("این فیلد نمی‌تواند خالی باشد")
        return value


PAGE = """<!doctype html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>درخواست وام</title>
  <style>
    :root { font-family: Tahoma, Arial, sans-serif; color: #172033; background: #f3f6fb; }
    * { box-sizing: border-box; }
    body { margin: 0; min-height: 100vh; display: grid; place-items: center; padding: 24px; }
    .card { width: min(760px, 100%); background: #fff; border-radius: 18px; padding: 30px; box-shadow: 0 12px 35px #263b5c1c; }
    h1 { margin: 0 0 8px; color: #173b72; font-size: 1.8rem; }
    .intro { margin: 0 0 24px; color: #5d6879; }
    form { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 17px; }
    label { display: flex; flex-direction: column; gap: 7px; font-weight: bold; font-size: .92rem; }
    input { width: 100%; border: 1px solid #ccd5e3; border-radius: 9px; padding: 11px 12px; font: inherit; direction: rtl; }
    input:focus { outline: 3px solid #d9e8ff; border-color: #3478d4; }
    .wide { grid-column: 1 / -1; }
    button { grid-column: 1 / -1; border: 0; border-radius: 9px; padding: 13px; background: #2167c5; color: white; font: inherit; font-weight: bold; cursor: pointer; }
    button:hover { background: #174f9b; }
    button:disabled { opacity: .65; cursor: wait; }
    #result { min-height: 24px; margin: 19px 0 0; font-weight: bold; }
    #result.success { color: #187044; } #result.error { color: #b42318; }
    @media (max-width: 580px) { form { grid-template-columns: 1fr; } .card { padding: 22px; } }
  </style>
</head>
<body>
  <main class="card">
    <h1>درخواست وام</h1>
    <p class="intro">لطفاً اطلاعات خود را برای بررسی درخواست وارد کنید.</p>
    <form id="loan-form" novalidate>
      <label>نام و نام خانوادگی
        <input id="full_name" name="full_name" type="text" required autocomplete="name">
      </label>
      <label>سن
        <input id="age" name="age" type="number" min="0" step="1" required>
      </label>
      <label>امتیاز
        <input id="score" name="score" type="number" min="0" step="any" required>
      </label>
      <label>میزان وام درخواستی
        <input id="requested_loan" name="requested_loan" type="number" min="0" step="any" required>
      </label>
      <label>حقوق
        <input id="salary" name="salary" type="number" min="0" step="any" required>
      </label>
      <label>کسر از حقوق
        <input id="salary_deduction" name="salary_deduction" type="number" min="0" step="any" required>
      </label>
      <label>مقدار وثیقه
        <input id="collateral" name="collateral" type="number" min="0" step="any" required>
      </label>
      <label>شغل
        <input id="occupation" name="occupation" type="text" required>
      </label>
      <label class="wide">سنوات کاری
        <input id="work_experience" name="work_experience" type="number" min="0" step="any" required>
      </label>
      <button id="submit-button" type="submit">تأیید</button>
    </form>
    <p id="result" role="status" aria-live="polite"></p>
  </main>
  <script>
    const form = document.getElementById('loan-form');
    const result = document.getElementById('result');
    const button = document.getElementById('submit-button');
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      if (!form.reportValidity()) return;
      result.textContent = 'در حال ارسال...';
      result.className = '';
      button.disabled = true;
      const data = Object.fromEntries(new FormData(form).entries());
      for (const key of ['age', 'score', 'requested_loan', 'salary', 'salary_deduction', 'collateral', 'work_experience']) {
        data[key] = Number(data[key]);
      }
      try {
        const response = await fetch('/api/loan-requests', {
          method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data)
        });
        const payload = await response.json();
        if (!response.ok) throw new Error(payload.detail ? 'لطفاً اطلاعات واردشده را بررسی کنید.' : 'ارسال ناموفق بود.');
        result.textContent = payload.message;
        result.className = 'success';
        form.reset();
      } catch (error) {
        result.textContent = error.message || 'خطا در ارتباط با سامانه.';
        result.className = 'error';
      } finally { button.disabled = false; }
    });
  </script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return PAGE


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/loan-requests")
def submit_loan_request(request: LoanRequest) -> dict[str, str]:
    return {"message": "درخواست وام شما با موفقیت ثبت شد."}
