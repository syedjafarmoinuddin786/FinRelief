from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.ai_service import analyze_financials

router = APIRouter()

class FinancialDataRequest(BaseModel):
    total_debt: float
    monthly_income: float
    monthly_expenses: float

class FinancialAdviceResponse(BaseModel):
    advice: str

@router.post("/analyze-debt", response_model=FinancialAdviceResponse)
async def analyze_debt(data: FinancialDataRequest):
    try:
        advice = analyze_financials(
            total_debt=data.total_debt,
            monthly_income=data.monthly_income,
            monthly_expenses=data.monthly_expenses
        )
        return FinancialAdviceResponse(advice=advice)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate advice: {str(e)}")
