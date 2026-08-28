from __future__ import annotations

import re

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator

app = FastAPI(title="فرم نمای کاربری")


class ContactPayload(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=2, max_length=100)
    email: str
    phone: str = Field(min_length=7, max_length=30)
    company: str = Field(min_length=2, max_length=120)
    job_title: str = Field(min_length=2, max_length=120)
    address: str = Field(min_length=5, max_length=250)
    city: str = Field(min_length=2, max_length=80)
    postal_code: str = Field(min_length=5, max_length=20)
    message: str = Field(min_length=5, max_length=1000)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
            raise ValueError("ایمیل نامعتبر است")
        return value


FORM_HTML = """<!doctype html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>فرم نمای کاربری</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.rtl.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
  <style>
    body { background: #f3f6fb; }
    .form-card { max-width: 900px; }
    .required::after { content: " *"; color: #dc3545; }
  </style>
</head>
<body>
  <main class="container py-5">
    <div class="row justify-content-center">
      <div class="col-12 form-card">
        <section class="card border-0 shadow-sm">
          <div class="card-body p-4 p-md-5">
            <h1 class="card-title h3 mb-2">فرم نمای کاربری</h1>
            <p class="text-secondary mb-4">لطفاً اطلاعات خود را برای ارتباط با ما وارد کنید.</p>
            <div id="status" class="alert d-none" role="alert" aria-live="polite"></div>
            <form id="profile-form" novalidate>
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label required" for="name">نام و نام خانوادگی</label>
                  <input class="form-control" id="name" name="name" type="text" required>
                </div>
                <div class="col-md-6">
                  <label class="form-label required" for="email">ایمیل</label>
                  <input class="form-control" id="email" name="email" type="email" required>
                </div>
                <div class="col-md-6">
                  <label class="form-label required" for="phone">شماره تماس</label>
                  <input class="form-control" id="phone" name="phone" type="tel" required>
                </div>
                <div class="col-md-6">
                  <label class="form-label required" for="company">نام شرکت</label>
                  <input class="form-control" id="company" name="company" type="text" required>
                </div>
                <div class="col-md-6">
                  <label class="form-label required" for="job_title">عنوان شغلی</label>
                  <input class="form-control" id="job_title" name="job_title" type="text" required>
                </div>
                <div class="col-md-6">
                  <label class="form-label required" for="city">شهر</label>
                  <input class="form-control" id="city" name="city" type="text" required>
                </div>
                <div class="col-12">
                  <label class="form-label required" for="address">نشانی</label>
                  <input class="form-control" id="address" name="address" type="text" required>
                </div>
                <div class="col-md-6">
                  <label class="form-label required" for="postal_code">کد پستی</label>
                  <input class="form-control" id="postal_code" name="postal_code" type="text" required>
                </div>
                <div class="col-12">
                  <label class="form-label required" for="message">پیام</label>
                  <textarea class="form-control" id="message" name="message" rows="4" required></textarea>
                </div>
                <div class="col-12 d-flex justify-content-start pt-2">
                  <button id="submit-button" class="btn btn-primary px-4" type="submit">ارسال فرم</button>
                </div>
              </div>
            </form>
          </div>
        </section>
      </div>
    </div>
  </main>
  <script>
    const form = document.getElementById('profile-form');
    const button = document.getElementById('submit-button');
    const statusBox = document.getElementById('status');

    function showStatus(message, kind) {
      statusBox.textContent = message;
      statusBox.className = `alert alert-${kind}`;
    }

    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      if (!form.checkValidity()) {
        form.classList.add('was-validated');
        showStatus('لطفاً همه فیلدهای ضروری را به‌درستی تکمیل کنید.', 'danger');
        return;
      }
      button.disabled = true;
      button.textContent = 'در حال ارسال...';
      statusBox.className = 'alert d-none';
      const payload = Object.fromEntries(new FormData(form).entries());
      try {
        const response = await fetch('/submit', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(payload)
        });
        const result = await response.json();
        if (!response.ok) throw new Error(result.detail || 'ارسال اطلاعات ناموفق بود.');
        showStatus(result.message, 'success');
        form.reset();
        form.classList.remove('was-validated');
      } catch (error) {
        showStatus(error.message || 'خطایی رخ داد. دوباره تلاش کنید.', 'danger');
      } finally {
        button.disabled = false;
        button.textContent = 'ارسال فرم';
      }
    });
  </script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def form_page() -> HTMLResponse:
    return HTMLResponse(FORM_HTML)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/submit")
def submit_form(payload: ContactPayload) -> dict[str, str]:
    return {"message": "اطلاعات شما با موفقیت ارسال شد."}
