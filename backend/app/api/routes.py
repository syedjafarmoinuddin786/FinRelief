from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.database import get_db
from app.db import crud
from app.core.security import create_access_token, verify_token
from app.services.ai_service import analyze_financials

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

class FinancialDataRequest(BaseModel):
    total_debt: float
    monthly_income: float
    monthly_expenses: float

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    income: float
    expenses: float

class Token(BaseModel):
    access_token: str
    token_type: str

class FinancialAdviceResponse(BaseModel):
    advice: str

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.post("/signup", response_model=Token)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud.create_user(db, user_data.name, user_data.email, user_data.password, user_data.income, user_data.expenses)
    access_token = create_access_token(data={"sub": user.Email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, form_data.username) # OAuth2 uses 'username' field for the email
    if not user or not crud.verify_password(form_data.password, user.Password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.Email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/analyze-debt", response_model=FinancialAdviceResponse)
async def analyze_debt(data: FinancialDataRequest, current_user = Depends(get_current_user)):
    try:
        advice = analyze_financials(
            total_debt=data.total_debt,
            monthly_income=data.monthly_income,
            monthly_expenses=data.monthly_expenses
        )
        return FinancialAdviceResponse(advice=advice)
    except Exception as e:
        # ai_service will raise specific exceptions, return them cleanly
        raise HTTPException(status_code=500, detail=str(e))
