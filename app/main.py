from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field


app = FastAPI(title="فرم درخواست وام")


class LoanRequest(BaseModel):
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    age: int = Field(..., ge=0)
    score: float = Field(..., ge=0)
    requested_loan: float = Field(..., ge=0)
    salary: float = Field(..., ge=0)
    salary_deduction: float = Field(..., ge=0)
    collateral_amount: float = Field(..., ge=0)
    job: str = Field(..., min_length=1)
    work_experience: float = Field(..., ge=0)


PAGE = """<!doctype html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>درخواست وام</title>
  <style>
    :root { font-family: Tahoma, Arial, sans-serif; color: #243044; background: #eef3f8; }
    * { box-sizing: border-box; }
    body { margin: 0; min-height: 100vh; display: grid; place-items: center; padding: 24px; }
    .card { width: min(760px, 100%); background: white; border-radius: 18px; padding: 28px; box-shadow: 0 12px 35px #263c551c; }
    h1 { margin: 0 0 24px; color: #163d67; font-size: 1.8rem; }
    form { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
    .field { display: flex; flex-direction: column; gap: 7px; }
    label { font-size: .92rem; font-weight: bold; }
    input { width: 100%; border: 1px solid #c8d3df; border-radius: 9px; padding: 11px; font: inherit; background: #fbfdff; }
    input:focus { outline: 2px solid #76a9d6; border-color: #397db5; }
    .actions { grid-column: 1 / -1; display: flex; align-items: center; gap: 14px; margin-top: 8px; }
    button { border: 0; border-radius: 9px; padding: 12px 30px; color: white; background: #1769aa; font: inherit; cursor: pointer; }
    button:disabled { opacity: .65; cursor: wait; }
    #message { min-height: 1.5em; font-size: .9rem; }
    #message.success { color: #147044; } #message.error { color: #b3261e; }
    @media (max-width: 600px) { form { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <main class="card">
    <h1>درخواست وام</h1>
    <form id="loan-form">
      <div class="field"><label for="first_name">نام</label><input id="first_name" name="first_name" type="text" required></div>
      <div class="field"><label for="last_name">نام خانوادگی</label><input id="last_name" name="last_name" type="text" required></div>
      <div class="field"><label for="age">سن</label><input id="age" name="age" type="number" min="0" required></div>
      <div class="field"><label for="score">امتیاز</label><input id="score" name="score" type="number" min="0" step="any" required></div>
      <div class="field"><label for="requested_loan">میزان وام درخواستی</label><input id="requested_loan" name="requested_loan" type="number" min="0" step="any" required></div>
      <div class="field"><label for="salary">حقوق</label><input id="salary" name="salary" type="number" min="0" step="any" required></div>
      <div class="field"><label for="salary_deduction">کسر از حقوق</label><input id="salary_deduction" name="salary_deduction" type="number" min="0" step="any" required></div>
      <div class="field"><label for="collateral_amount">مقدار وثیقه</label><input id="collateral_amount" name="collateral_amount" type="number" min="0" step="any" required></div>
      <div class="field"><label for="job">شغل</label><input id="job" name="job" type="text" required></div>
      <div class="field"><label for="work_experience">سنوات کاری</label><input id="work_experience" name="work_experience" type="number" min="0" step="any" required></div>
      <div class="actions">
        <button id="submit-button" type="submit">تایید</button>
        <span id="message" role="status" aria-live="polite"></span>
      </div>
    </form>
  </main>
  <script>
    const form = document.getElementById('loan-form');
    const button = document.getElementById('submit-button');
    const message = document.getElementById('message');
    const numericFields = ['age', 'score', 'requested_loan', 'salary', 'salary_deduction', 'collateral_amount', 'work_experience'];

    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      if (!form.checkValidity()) { form.reportValidity(); return; }
      const data = Object.fromEntries(new FormData(form).entries());
      numericFields.forEach((name) => { data[name] = Number(data[name]); });
      button.disabled = true;
      message.className = '';
      message.textContent = 'در حال ارسال...';
      try {
        const response = await fetch('/api/loan-requests', {
          method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data)
        });
        const result = await response.json();
        if (!response.ok) throw new Error('اطلاعات واردشده معتبر نیست.');
        message.className = 'success';
        message.textContent = result.message;
      } catch (error) {
        message.className = 'error';
        message.textContent = error.message || 'خطا در ارسال درخواست.';
      } finally { button.disabled = false; }
    });
  </script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def loan_form() -> HTMLResponse:
    return HTMLResponse(PAGE)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/loan-requests")
def submit_loan_request(request: LoanRequest) -> dict[str, str]:
    return {"message": "درخواست وام شما با موفقیت ثبت شد."}
