# فرم بازخورد

یک فرم بازخورد فارسی و راست‌به‌چپ با FastAPI و JavaScript خام.

## اجرا

```text
uvicorn app.main:app
```

صفحه فرم در `/`، بررسی سلامت در `/health` و endpoint ارسال در `POST /api/feedback` قرار دارد.

بدنه درخواست نمونه:

```json
{
  "name": "کاربر نمونه",
  "email": "user@example.com",
  "message": "تجربه خوبی بود.",
  "rating": 5
}
```

`rating` باید عدد صحیح strict بین ۱ و ۵ باشد؛ مقدار اعشاری، رشته‌ای، بولی یا خارج از این بازه پذیرفته نمی‌شود.

## تست

```text
python -m pytest -q
python -m compileall -q .
```
