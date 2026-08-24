# Red Background Demo

یک برنامه کوچک FastAPI که صفحه اصلی آن از stylesheet محلی `app.css` استفاده می‌کند.

## اجرا

نقطه ورود ASGI برنامه `app.main:app` است. برای اجرای محلی با یک سرور ASGI:

```text
uvicorn app.main:app
```

مسیرهای موجود:

- `GET /` — صفحه اصلی
- `GET /app.css` — فایل CSS محلی
- `GET /health` — پاسخ JSON سلامت

رنگ پس‌زمینه عنصر `body` در `app.css` برابر `red` است.

## تست

```text
pytest
```
