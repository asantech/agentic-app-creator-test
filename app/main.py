from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

app = FastAPI(title="درخواست وام")


class LoanRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    phone: str = Field(min_length=7, max_length=20)
    amount: int = Field(gt=0, le=10_000_000_000)
    employment: str = Field(min_length=2, max_length=80)


PAGE = """<!doctype html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>درخواست وام</title>
  <style>
    :root {
      color-scheme: light;
      font-family: Tahoma, Arial, sans-serif;
      color: #172033;
      background: #f4f7fb;
    }
    * { box-sizing: border-box; }
    body {
      direction: rtl;
      margin: 0;
      min-height: 100vh;
      background: linear-gradient(135deg, #f8fbff, #e7eef8);
    }
    .page {
      min-height: 100vh;
      display: flex;
      justify-content: flex-end;
      align-items: center;
      padding: 32px 7vw 32px 10vw;
    }
    .form-card {
      width: min(100%, 500px);
      margin-left: auto;
      padding: 32px;
      border: 1px solid #dbe4f0;
      border-radius: 18px;
      background: #fff;
      box-shadow: 0 16px 45px rgba(35, 67, 110, .12);
    }
    h1 { margin: 0 0 26px; font-size: 1.8rem; color: #102a56; }
    .field { margin-bottom: 18px; }
    label { display: block; margin-bottom: 7px; font-size: .95rem; font-weight: bold; }
    input, select {
      width: 100%;
      border: 1px solid #cbd7e6;
      border-radius: 9px;
      padding: 12px;
      font: inherit;
      background: #fbfdff;
    }
    input:focus, select:focus { outline: 2px solid #8eb5ed; border-color: #3576c6; }
    button {
      width: 100%;
      border: 0;
      border-radius: 9px;
      padding: 13px;
      color: white;
      background: #1769aa;
      font: inherit;
      font-weight: bold;
      cursor: pointer;
    }
    button:hover { background: #12588f; }
    button:disabled { opacity: .65; cursor: wait; }
    #status { min-height: 24px; margin: 16px 0 0; font-size: .9rem; }
    .success { color: #18733b; }
    .error { color: #b42318; }
    @media (max-width: 650px) {
      .page { padding: 20px; }
      .form-card { padding: 24px; }
    }
  </style>
</head>
<body>
  <main class="page">
    <section class="form-card" aria-labelledby="form-title">
      <h1 id="form-title">درخواست وام</h1>
      <form id="loan-form">
        <div class="field">
          <label for="full-name">نام و نام خانوادگی</label>
          <input id="full-name" name="full_name" type="text" required minlength="2" autocomplete="name">
        </div>
        <div class="field">
          <label for="phone">شماره تماس</label>
          <input id="phone" name="phone" type="tel" required minlength="7" autocomplete="tel">
        </div>
        <div class="field">
          <label for="amount">مبلغ وام (تومان)</label>
          <input id="amount" name="amount" type="number" required min="1" step="100000">
        </div>
        <div class="field">
          <label for="employment">وضعیت شغلی</label>
          <select id="employment" name="employment" required>
            <option value="">انتخاب کنید</option>
            <option value="شاغل">شاغل</option>
            <option value="آزاد">آزاد</option>
            <option value="بازنشسته">بازنشسته</option>
            <option value="سایر">سایر</option>
          </select>
        </div>
        <button type="submit">ارسال</button>
        <p id="status" role="status" aria-live="polite"></p>
      </form>
    </section>
  </main>
  <script>
    const form = document.getElementById('loan-form');
    const status = document.getElementById('status');
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const data = new FormData(form);
      const payload = {
        full_name: data.get('full_name'),
        phone: data.get('phone'),
        amount: Number(data.get('amount')),
        employment: data.get('employment')
      };
      status.className = '';
      status.textContent = 'در حال ارسال...';
      const button = form.querySelector('button');
      button.disabled = true;
      try {
        const response = await fetch('/api/loan-request', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(payload)
        });
        if (!response.ok) throw new Error('request failed');
        status.className = 'success';
        status.textContent = 'درخواست شما با موفقیت ثبت شد.';
        form.reset();
      } catch (error) {
        status.className = 'error';
        status.textContent = 'ثبت درخواست انجام نشد. دوباره تلاش کنید.';
      } finally {
        button.disabled = false;
      }
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


@app.post("/api/loan-request")
def submit_loan_request(request: LoanRequest) -> dict[str, str]:
    return {"status": "accepted", "message": "درخواست وام دریافت شد."}
