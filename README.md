# Purple Color Demo

یک برنامه کوچک FastAPI که صفحه اصلی آن از `app.css` استفاده می‌کند. مقدار ویژگی CSS به نام `color` در این فایل برابر `purple` است.

## اجرا

نقطه ورود ASGI برنامه:

```text
app.main:app
```

برای اجرای محلی با یک سرور ASGI مانند Uvicorn:

```text
uvicorn app.main:app
```

مسیرهای موجود:

- `GET /` صفحه اصلی
- `GET /app.css` فایل stylesheet
- `GET /health` پاسخ سلامت JSON

## تست

```text
pytest
```
