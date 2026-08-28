# فرم نمای کاربری

این پروژه یک فرم فارسی راست‌به‌چپ با FastAPI و Bootstrap است. Bootstrap فقط به‌صورت stylesheet از CDN در HTML ارجاع داده شده و هیچ وابستگی Python جدیدی لازم نیست.

## اجرا

```text
uvicorn app.main:app --reload
```

صفحه فرم در `/`، endpoint سلامت در `/health` و endpoint ارسال در `/submit` قرار دارد.

## قرارداد ارسال

`POST /submit` با بدنه JSON شامل این ۹ فیلد انجام می‌شود:

`name`, `email`, `phone`, `company`, `job_title`, `address`, `city`, `postal_code`, `message`

ارسال فرم در مرورگر با `fetch` انجام می‌شود و نتیجه در alert بوت‌استرپ نمایش داده می‌شود.

## تست

```text
pytest
python -m compileall app tests
```
