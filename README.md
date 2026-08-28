# فرم درخواست وام

یک فرم ساده فارسی و راست‌چین با FastAPI برای دریافت اطلاعات درخواست وام.

## اجرا

از ریشه پروژه اجرا کنید:

```text
uvicorn app.main:app --reload
```

سپس صفحه را در مسیر `/` باز کنید. بررسی سلامت برنامه در `/health` و endpoint ارسال فرم در مسیر زیر در دسترس است:

```text
POST /api/loan-requests
```

بدنه درخواست باید JSON شامل این فیلدها باشد:

- `full_name`
- `age`
- `score`
- `requested_loan`
- `salary`
- `salary_deduction`
- `collateral`
- `job`
- `work_years`

تمام فیلدها الزامی هستند و فیلدهای عددی نباید منفی باشند.

## تست

```text
python -m pytest -q
python -m compileall -q .
```

رابط کاربری با HTML، CSS و JavaScript خام ساخته شده و ارسال فرم بدون بارگذاری مجدد صفحه انجام می‌شود.
