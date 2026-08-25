# فرم درخواست وام

یک صفحه ساده فارسی با FastAPI، HTML، CSS و JavaScript خام.

## اجرا

```text
uvicorn app.main:app
```

صفحه فرم در مسیر `/` و بررسی سلامت سرویس در مسیر `/health` قرار دارد. ارسال فرم به `POST /api/loan-request` انجام می‌شود.

## تست

```text
python -m pytest -q --disable-warnings --maxfail=1
```
