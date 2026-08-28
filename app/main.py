from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

app = FastAPI(title="فرم درخواست وام")


class LoanRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=120)
    age: float = Field(ge=0)
    score: float = Field(ge=0)
    requested_loan: float = Field(ge=0)
    salary: float = Field(ge=0)
    salary_deduction: float = Field(ge=0)
    collateral: float = Field(ge=0)
    occupation: str = Field(min_length=1, max_length=120)
    work_experience: float = Field(ge=0)


PAGE = '''<!doctype html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>درخواست وام</title>
  <style>
    :root { font-family: Tahoma, Arial, sans-serif; color: #172033; background: #f3f6fb; }
    * { box-sizing: border-box; }
    body { margin: 0; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 24px; }
    .card { width: min(760px, 100%); background: white; border-radius: 18px; padding: 30px; box-shadow: 0 12px 35px rgba(26, 54, 93, .12); }
    h1 { margin: 0 0 8px; color: #173b72; font-size: 1.8rem; }
    .intro { margin: 0 0 24px; color: #64748b; }
    .grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; }
    label { display: flex; flex-direction: column; gap: 7px; font-weight: bold; font-size: .92rem; }
    input { width: 100%; border: 1px solid #cbd5e1; border-radius: 9px; padding: 12px; font: inherit; direction: rtl; }
    input:focus { outline: 3px solid #bfdbfe; border-color: #2563eb; }
    button { margin-top: 24px; width: 100%; border: 0; border-radius: 9px; padding: 13px; color: white; background: #2563eb; font: inherit; font-weight: bold; cursor: pointer; }
    button:hover { background: #1d4ed8; }
    button:disabled { opacity: .65; cursor: wait; }
    #status { min-height: 24px; margin: 16px 0 0; font-weight: bold; }
    #status.success { color: #15803d; }
    #status.error { color: #b91c1c; }
    @media (max-width: 600px) { .card { padding: 22px; } .grid { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <main class="card">
    <h1>درخواست وام</h1>
    <p class="intro">لطفاً اطلاعات خود را برای بررسی درخواست وارد کنید.</p>
    <form id="loan-form">
      <div class="grid">
        <label>نام و نام خانوادگی<input name="full_name" type="text" required maxlength="120"></label>
        <label>سن<input name="age" type="number" min="0" step="any" required></label>
        <label>امتیاز<input name="score" type="number" min="0" step="any" required></label>
        <label>میزان وام درخواستی<input name="requested_loan" type="number" min="0" step="any" required></label>
        <label>حقوق<input name="salary" type="number" min="0" step="any" required></label>
        <label>کسر از حقوق<input name="salary_deduction" type="number" min="0" step="any" required></label>
        <label>مقدار وثیقه<input name="collateral" type="number" min="0" step="any" required></label>
        <label>شغل<input name="occupation" type="text" required maxlength="120"></label>
        <label>سنوات کاری<input name="work_experience" type="number" min="0" step="any" required></label>
      </div>
      <button id="submit-button" type="submit">تایید</button>
      <p id="status" role="status" aria-live="polite"></p>
    </form>
  </main>
  <script>
    const form = document.getElementById('loan-form');
    const button = document.getElementById('submit-button');
    const status = document.getElementById('status');
    const numericFields = ['age', 'score', 'requested_loan', 'salary', 'salary_deduction', 'collateral', 'work_experience'];

    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const data = Object.fromEntries(new FormData(form).entries());
      numericFields.forEach((field) => { data[field] = Number(data[field]); });
      button.disabled = true;
      button.textContent = 'در حال ارسال...';
      status.textContent = '';
      status.className = '';
      try {
        const response = await fetch('/api/loan-requests', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        });
        const result = await response.json();
        if (!response.ok) throw new Error(result.detail ? 'لطفاً مقادیر واردشده را بررسی کنید.' : 'ارسال ناموفق بود.');
        status.textContent = result.message;
        status.className = 'success';
      } catch (error) {
        status.textContent = error.message || 'خطایی رخ داد.';
        status.className = 'error';
      } finally {
        button.disabled = false;
        button.textContent = 'تایید';
      }
    });
  </script>
</body>
</html>'''


@app.get("/", response_class=HTMLResponse)
def loan_form() -> str:
    return PAGE


@app.post("/api/loan-requests")
def create_loan_request(request: LoanRequest) -> dict[str, object]:
    return {
        "success": True,
        "message": "درخواست وام شما با موفقیت ثبت شد.",
        "data": request.model_dump(),
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
