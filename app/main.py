from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from starlette.staticfiles import StaticFiles


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="فرم درخواست وام")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class LoanRequest(BaseModel):
    full_name: str = Field(..., min_length=1, description="نام و نام خانوادگی")
    age: float = Field(..., ge=0, description="سن")
    score: float = Field(..., ge=0, description="امتیاز")
    requested_loan: float = Field(..., ge=0, description="میزان وام درخواستی")
    salary: float = Field(..., ge=0, description="حقوق")
    salary_deduction: float = Field(..., ge=0, description="کسر از حقوق")
    collateral: float = Field(..., ge=0, description="مقدار وثیقه")
    job: str = Field(..., min_length=1, description="شغل")
    work_years: float = Field(..., ge=0, description="سنوات کاری")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=FileResponse)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html", media_type="text/html; charset=utf-8")


@app.post("/api/loan-requests")
def create_loan_request(request: LoanRequest) -> dict[str, object]:
    return {
        "success": True,
        "message": "درخواست وام با موفقیت ثبت شد.",
        "data": request.model_dump(),
    }
