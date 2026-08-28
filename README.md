# ابزار امن حذف فایل‌های مخزن

این برنامه ابتدا فهرست فرزندان ریشهٔ مخزن را در `GET /api/preview` نمایش می‌دهد و فقط با `POST /api/delete` و JSON زیر حذف واقعی را انجام می‌دهد:

```json
{"confirmation": true}
```

ریشه باید صریحاً با متغیرهای محیطی `REPOSITORY_ROOT` و `SANDBOX_ROOT` تنظیم شود؛ ریشه باید یک پوشهٔ موجود و بدون symlink درون sandbox باشد. برای نمونه:

```text
SANDBOX_ROOT=/tmp/sandbox REPOSITORY_ROOT=/tmp/sandbox/repository uvicorn app.main:app
```

خود ریشه و `.git` حفظ می‌شوند. هر symlink در مسیر ریشه یا محتوای قابل حذف باعث رد امن عملیات می‌شود.

آزمون‌ها با `pytest` اجرا می‌شوند و از ابزار خارجی یا سرویس شبکه استفاده نمی‌کنند.
