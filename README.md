# فرم درخواست وام

یک وب‌اپلیکیشن کوچک فارسی و راست‌به‌چپ با FastAPI و Vanilla JavaScript است.

## اجرا

ورودی ASGI برنامه `app.main:app` است. برای اجرای محلی با Uvicorn:

```text
uvicorn app.main:app --reload
```

سپس صفحه اصلی را در مسیر `/` و وضعیت سرویس را در `/health` مشاهده کنید.

## آزمون

```text
pytest
```

فرم اطلاعات را با `fetch` به endpoint داخلی `POST /api/loan-requests` ارسال می‌کند و اعتبارسنجی داده‌ها در سمت سرور با Pydantic انجام می‌شود.
