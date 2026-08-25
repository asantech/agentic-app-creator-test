from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, conint


app = FastAPI(title="فرم بازخورد")


class FeedbackRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=3, max_length=200)
    message: str = Field(..., min_length=1, max_length=2000)
    rating: conint(strict=True, ge=1, le=5)


PAGE = """<!doctype html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>فرم بازخورد</title>
  <style>
    :root { font-family: Tahoma, Arial, sans-serif; color: #243047; background: #f4f7fb; }
    * { box-sizing: border-box; }
    body { margin: 0; min-height: 100vh; display: grid; place-items: center; padding: 24px; }
    .card { width: min(100%, 560px); background: white; border-radius: 14px; padding: 28px; box-shadow: 0 8px 28px #24304718; }
    h1 { margin-top: 0; font-size: 1.55rem; }
    .field { margin: 16px 0; }
    label { display: block; margin-bottom: 7px; font-weight: 600; }
    input, textarea { width: 100%; border: 1px solid #cbd5e1; border-radius: 8px; padding: 11px; font: inherit; }
    textarea { min-height: 110px; resize: vertical; }
    input:focus, textarea:focus { outline: 2px solid #93c5fd; border-color: #2563eb; }
    button { width: 100%; border: 0; border-radius: 8px; padding: 12px; color: white; background: #2563eb; font: inherit; cursor: pointer; }
    button:disabled { opacity: .65; cursor: wait; }
    .error { min-height: 24px; color: #b91c1c; margin: 12px 0 0; }
    .success { color: #166534; margin: 12px 0 0; }
  </style>
</head>
<body>
  <main class="card">
    <h1>ارسال بازخورد</h1>
    <form id="feedback-form" novalidate>
      <div class="field">
        <label for="name">نام</label>
        <input id="name" name="name" type="text" required maxlength="100">
      </div>
      <div class="field">
        <label for="email">ایمیل</label>
        <input id="email" name="email" type="email" required maxlength="200">
      </div>
      <div class="field">
        <label for="message">پیام</label>
        <textarea id="message" name="message" required maxlength="2000"></textarea>
      </div>
      <div class="field">
        <label for="rating">امتیاز (۱ تا ۵)</label>
        <input id="rating" name="rating" type="number" min="1" max="5" step="1" required inputmode="numeric" aria-describedby="form-error">
      </div>
      <button id="submit-button" type="submit">ارسال بازخورد</button>
      <p id="form-error" class="error" role="alert"></p>
      <p id="form-success" class="success" role="status"></p>
    </form>
  </main>
  <script>
    const form = document.getElementById('feedback-form');
    const errorBox = document.getElementById('form-error');
    const successBox = document.getElementById('form-success');
    const submitButton = document.getElementById('submit-button');

    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      errorBox.textContent = '';
      successBox.textContent = '';
      const ratingValue = Number(document.getElementById('rating').value);
      if (!Number.isInteger(ratingValue) || ratingValue < 1 || ratingValue > 5) {
        errorBox.textContent = 'لطفاً امتیازی صحیح بین ۱ تا ۵ وارد کنید.';
        return;
      }
      const payload = {
        name: document.getElementById('name').value.trim(),
        email: document.getElementById('email').value.trim(),
        message: document.getElementById('message').value.trim(),
        rating: ratingValue
      };
      if (!payload.name || !payload.email || !payload.message) {
        errorBox.textContent = 'لطفاً همه فیلدها را تکمیل کنید.';
        return;
      }
      submitButton.disabled = true;
      try {
        const response = await fetch('/api/feedback', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const result = await response.json();
        if (!response.ok) {
          errorBox.textContent = 'اطلاعات واردشده معتبر نیست؛ لطفاً فیلدها را بررسی کنید.';
          return;
        }
        successBox.textContent = result.message;
        form.reset();
      } catch (error) {
        errorBox.textContent = 'ارسال انجام نشد؛ لطفاً دوباره تلاش کنید.';
      } finally {
        submitButton.disabled = false;
      }
    });
  </script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def homepage() -> str:
    return PAGE


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/feedback")
def submit_feedback(feedback: FeedbackRequest) -> dict[str, object]:
    return {
        "message": "بازخورد شما با موفقیت دریافت شد.",
        "data": feedback.model_dump() if hasattr(feedback, "model_dump") else feedback.dict(),
    }
