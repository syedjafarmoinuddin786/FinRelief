from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from typing import List, Optional
from datetime import datetime
import re
import pyotp
import qrcode
import io
import base64
from app.db.database import get_db
from app.db import crud, models
from app.core.security import create_access_token, verify_token
from app.services.ai_service import compute_financial_metrics, generate_settlement_recommendation, generate_negotiation_letter

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

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
    if payload.get("2fa_pending"):
        raise HTTPException(status_code=403, detail="2FA verification required")
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# --------------------------
# PyDantic Models (A05 Validation)
# --------------------------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    income: float = Field(..., gt=0)
    expenses: float = Field(..., ge=0)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if not re.search(r"[a-zA-Z]", v):
            raise ValueError("Password must contain at least one letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[@$!%*?&#]", v):
            raise ValueError("Password must contain at least one special character")
        return v

class Token(BaseModel):
    access_token: str
    token_type: str
    requires_2fa: Optional[bool] = False

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: str
    new_password: str = Field(..., min_length=8)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v):
        if not re.search(r"[a-zA-Z]", v):
            raise ValueError("Password must contain at least one letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[@$!%*?&#]", v):
            raise ValueError("Password must contain at least one special character")
        return v

class Verify2FARequest(BaseModel):
    token: str 
    code: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v):
        if not re.search(r"[a-zA-Z]", v):
            raise ValueError("Password must contain at least one letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[@$!%*?&#]", v):
            raise ValueError("Password must contain at least one special character")
        return v

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    income: Optional[float] = None
    expenses: Optional[float] = None
    credit_score: Optional[int] = None
    savings: Optional[float] = None
    employment_status: Optional[str] = None
    financial_goals: Optional[str] = None

class UserProfileResponse(BaseModel):
    Name: str
    Email: str
    MonthlyIncome: float
    MonthlyExpenses: float
    CreditScore: Optional[int]
    Savings: Optional[float]
    EmploymentStatus: Optional[str]
    FinancialGoals: Optional[str]
    model_config = ConfigDict(from_attributes=True)

class SettingsUpdate(BaseModel):
    theme: str
    currency: str
    language: str
    notifications_enabled: bool

class SettingsResponse(BaseModel):
    Theme: str
    Currency: str
    Language: str
    NotificationsEnabled: bool
    model_config = ConfigDict(from_attributes=True)

class LoanCreate(BaseModel):
    lender_name: str
    loan_type: str
    outstanding_amount: float = Field(..., gt=0)
    interest_rate: float = Field(..., ge=0)
    emi: float = Field(..., ge=0)
    overdue_months: int = Field(..., ge=0)
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    status: Optional[str] = "Active"

class LoanResponse(BaseModel):
    LoanID: int
    UserID: int
    LenderName: str
    LoanType: str
    OutstandingAmount: float
    InterestRate: float
    EMI: float
    OverdueMonths: int
    StartDate: Optional[datetime] = None
    DueDate: Optional[datetime] = None
    Status: str = "Active"
    model_config = ConfigDict(from_attributes=True)

class NegotiationRequest(BaseModel):
    tone: str = Field("professional", pattern="^(professional|firm|conciliatory)$")

class SettlementResponse(BaseModel):
    emi_ratio: float
    dti_ratio: float
    monthly_surplus: float
    stress_level: str
    suggested_settlement: float
    narrative: str

class NegotiationResponse(BaseModel):
    strategy: str
    letter: str

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

# --------------------------
# Auth Routes
# --------------------------
from slowapi import Limiter
from slowapi.util import get_remote_address
limiter = Limiter(key_func=get_remote_address)

@router.post("/signup", response_model=Token)
@limiter.limit("3/minute")
async def signup(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud.create_user(db, user_data.name, user_data.email, user_data.password, user_data.income, user_data.expenses)
    
    access_token = create_access_token(data={"sub": user.Email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, form_data.username) 
    if not user or not crud.verify_password(form_data.password, user.Password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        
    if user.is_2fa_enabled:
        access_token = create_access_token(data={"sub": user.Email, "2fa_pending": True})
        return {"access_token": access_token, "token_type": "bearer", "requires_2fa": True}
        
    access_token = create_access_token(data={"sub": user.Email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/verify-email")
async def verify_email(token: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_verification_token(db, token)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
    crud.verify_email(db, user)
    # Return HTML so user can click it in browser
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content="<h1>Email successfully verified!</h1><p>You can now go back and log in.</p>")

@router.post("/forgot-password")
@limiter.limit("3/minute")
async def forgot_password(request: Request, req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, req.email)
    if user:
        code = crud.set_reset_token(db, user)
        print(f"\n\n--- PASSWORD RESET CODE (MOCK EMAIL) ---\nYour 6-digit code is: {code}\n----------------------------------------\n\n")
    return {"message": "If that email is registered, a reset code has been sent (check console)."}

@router.post("/reset-password")
async def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_reset_token(db, req.email, req.code)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset code")
    crud.reset_password(db, user, req.new_password)
    return {"message": "Password has been reset successfully"}

@router.post("/2fa/setup")
async def setup_2fa(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.is_2fa_enabled:
        raise HTTPException(status_code=400, detail="2FA is already enabled")
    
    secret = pyotp.random_base32()
    crud.set_totp_secret(db, current_user, secret)
    
    uri = pyotp.totp.TOTP(secret).provisioning_uri(name=current_user.Email, issuer_name="FinRelief")
    qr = qrcode.make(uri)
    buf = io.BytesIO()
    qr.save(buf, format="PNG")
    qr_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    return {"qr_code": f"data:image/png;base64,{qr_b64}", "secret": secret}

@router.post("/2fa/enable")
async def enable_2fa(req: Verify2FARequest, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # When enabling 2FA, the token field can just be ignored since they are already fully authenticated
    totp = pyotp.TOTP(current_user.totp_secret)
    if not totp.verify(req.code):
        raise HTTPException(status_code=400, detail="Invalid 2FA code")
    crud.enable_2fa(db, current_user)
    return {"message": "2FA has been enabled successfully"}

@router.post("/2fa/verify", response_model=Token)
async def verify_2fa(req: Verify2FARequest, db: Session = Depends(get_db)):
    payload = verify_token(req.token)
    if not payload or not payload.get("2fa_pending"):
        raise HTTPException(status_code=401, detail="Invalid or expired temporary token")
        
    user = crud.get_user_by_email(db, payload.get("sub"))
    if not user or not user.is_2fa_enabled:
        raise HTTPException(status_code=400, detail="User not found or 2FA not enabled")
        
    totp = pyotp.TOTP(user.totp_secret)
    if not totp.verify(req.code):
        raise HTTPException(status_code=400, detail="Invalid 2FA code")
        
    access_token = create_access_token(data={"sub": user.Email})
    return {"access_token": access_token, "token_type": "bearer"}

# --------------------------
# User Profile & Settings
# --------------------------
@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return current_user

@router.put("/profile", response_model=UserProfileResponse)
async def update_profile(profile_data: UserProfileUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    updated_user = crud.update_user_profile(db, current_user, profile_data.model_dump(exclude_unset=True))
    return updated_user

@router.post("/change-password")
async def change_password(req: ChangePasswordRequest, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not crud.verify_password(req.old_password, current_user.Password):
        raise HTTPException(status_code=400, detail="Incorrect old password")
    crud.update_user_password(db, current_user, req.new_password)
    return {"message": "Password changed successfully"}

@router.get("/settings", response_model=SettingsResponse)
async def get_settings(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.get_user_settings(db, current_user.UserID)

@router.put("/settings", response_model=SettingsResponse)
async def update_settings(settings_data: SettingsUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    setting = crud.get_user_settings(db, current_user.UserID)
    return crud.update_user_settings(
        db, setting, settings_data.theme, settings_data.currency, 
        settings_data.language, settings_data.notifications_enabled
    )

# --------------------------
# Loan Routes
# --------------------------
@router.post("/loans", response_model=LoanResponse)
async def create_loan(loan_data: LoanCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    loan = crud.create_loan(
        db, current_user.UserID, loan_data.lender_name, loan_data.loan_type,
        loan_data.outstanding_amount, loan_data.interest_rate, loan_data.emi, loan_data.overdue_months,
        loan_data.start_date, loan_data.due_date, loan_data.status
    )
    return loan

@router.get("/loans", response_model=List[LoanResponse])
async def get_loans(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.get_user_loans(db, current_user.UserID)

@router.get("/loans/{loan_id}", response_model=LoanResponse)
async def get_loan(loan_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    loan = crud.get_loan_by_id(db, loan_id, current_user.UserID)
    return loan

@router.put("/loans/{loan_id}", response_model=LoanResponse)
async def update_loan(loan_id: int, loan_data: LoanCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    loan = crud.get_loan_by_id(db, loan_id, current_user.UserID)
    return crud.update_loan(db, loan, loan_data.model_dump(exclude_unset=True))

@router.delete("/loans/{loan_id}")
async def delete_loan(loan_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    loan = crud.get_loan_by_id(db, loan_id, current_user.UserID)
    crud.delete_loan(db, loan)
    return {"message": "Loan deleted successfully"}

# --------------------------
# Chatbot Routes
# --------------------------
@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    loans = crud.get_loans_for_user(db, current_user.UserID)
    total_debt = sum(l.OutstandingAmount for l in loans)
    
    from app.services.ai_service import chat_with_advisor
    ai_response = chat_with_advisor(req.message, current_user.Name, total_debt)
    
    return {"response": ai_response}

# --------------------------
# Scenario 1: Settlement Recommendation
# --------------------------
@router.post("/loans/{loan_id}/settlement-recommendation", response_model=SettlementResponse)
async def get_settlement_recommendation(loan_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    loan = crud.get_loan_by_id(db, loan_id, current_user.UserID)
    
    # 1. Deterministic Math
    metrics = compute_financial_metrics(
        outstanding_amount=loan.OutstandingAmount,
        monthly_income=current_user.MonthlyIncome,
        monthly_expenses=current_user.MonthlyExpenses,
        loan_emi=loan.EMI,
        overdue_months=loan.OverdueMonths
    )
    
    # 2. Persist to FinancialProfile
    crud.upsert_financial_profile(
        db, current_user.UserID, metrics["emi_ratio"], metrics["dti_ratio"], 
        metrics["monthly_surplus"], metrics["stress_level"]
    )
    
    # 3. Persist to SettlementPrediction
    crud.create_settlement_prediction(
        db, loan.LoanID, metrics["suggested_settlement"], 
        metrics["stress_level"], metrics["suggested_settlement"]
    )
    
    # 4. Generate Narrative
    narrative = generate_settlement_recommendation(
        lender_name=loan.LenderName, loan_type=loan.LoanType, outstanding_amount=loan.OutstandingAmount,
        overdue_months=loan.OverdueMonths, emi_ratio=metrics["emi_ratio"], dti_ratio=metrics["dti_ratio"],
        monthly_surplus=metrics["monthly_surplus"], stress_level=metrics["stress_level"], 
        suggested_settlement=metrics["suggested_settlement"]
    )
    
    # Log AI History
    crud.create_ai_history(db, current_user.UserID, narrative, "Settlement Recommendation")
    
    return SettlementResponse(**metrics, narrative=narrative)

# --------------------------
# Scenario 2: Negotiation Letter
# --------------------------
@router.post("/loans/{loan_id}/negotiation-letter", response_model=NegotiationResponse)
async def create_negotiation_letter(loan_id: int, request_data: NegotiationRequest, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    loan = crud.get_loan_by_id(db, loan_id, current_user.UserID)
    
    # Recalculate metrics just for surplus/settlement to feed the prompt
    metrics = compute_financial_metrics(
        outstanding_amount=loan.OutstandingAmount, monthly_income=current_user.MonthlyIncome,
        monthly_expenses=current_user.MonthlyExpenses, loan_emi=loan.EMI, overdue_months=loan.OverdueMonths
    )
    
    # Generate Strategy & Letter
    result = generate_negotiation_letter(
        borrower_name=current_user.Name, lender_name=loan.LenderName, loan_type=loan.LoanType,
        outstanding_amount=loan.OutstandingAmount, overdue_months=loan.OverdueMonths,
        monthly_surplus=metrics["monthly_surplus"], suggested_settlement=metrics["suggested_settlement"],
        tone=request_data.tone
    )
    
    # Persist AINegotiation
    crud.create_ai_negotiation(
        db, current_user.UserID, loan.LoanID, result["strategy"], result["letter"]
    )
    
    crud.create_ai_history(db, current_user.UserID, result["letter"], "Negotiation Letter")
    
    return NegotiationResponse(strategy=result["strategy"], letter=result["letter"])

# --------------------------
# Scenario 3: History & Dashboard
# --------------------------
@router.get("/dashboard")
async def get_dashboard(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = crud.get_financial_profile(db, current_user.UserID)
    loans = crud.get_user_loans(db, current_user.UserID)
    recent_history = crud.get_user_ai_history(db, current_user.UserID)[:5]
    
    total_debt = 0.0
    total_emi = 0.0
    total_interest = 0.0
    active_loans = 0
    overdue_loans = 0
    
    loan_data = []
    for loan in loans:
        total_debt += loan.OutstandingAmount or 0
        total_emi += loan.EMI or 0
        # rough estimation of yearly interest
        total_interest += (loan.OutstandingAmount or 0) * ((loan.InterestRate or 0) / 100.0)
        
        if loan.OverdueMonths and loan.OverdueMonths > 0:
            overdue_loans += 1
        elif loan.Status and loan.Status.lower() == "active":
            active_loans += 1
            
        predictions = crud.get_loan_settlement_predictions(db, loan.LoanID)
        latest_pred = predictions[0].SuggestedSettlement if predictions else None
        loan_data.append({
            "LoanID": loan.LoanID,
            "LenderName": loan.LenderName,
            "LoanType": loan.LoanType,
            "OutstandingAmount": loan.OutstandingAmount,
            "EMI": loan.EMI,
            "Status": loan.Status,
            "OverdueMonths": loan.OverdueMonths,
            "LatestSettlementPrediction": latest_pred
        })
        
    return {
        "profile": profile,
        "loans": loan_data,
        "summary": {
            "total_debt": total_debt,
            "total_emi": total_emi,
            "total_interest": total_interest,
            "active_loans": active_loans,
            "overdue_loans": overdue_loans,
            "monthly_income": current_user.MonthlyIncome or 0,
            "monthly_expenses": current_user.MonthlyExpenses or 0,
            "monthly_surplus": profile.MonthlySurplus if profile else 0,
            "stress_level": profile.StressLevel if profile else "Unknown"
        },
        "recent_ai_activity": [{"type": h.QueryType, "date": h.Timestamp} for h in recent_history],
        "recent_history": recent_history
    }

# --------------------------
# Payoff Planner
# --------------------------
@router.get("/payoff-planner")
async def get_payoff_planner(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    loans = crud.get_user_loans(db, current_user.UserID)
    profile = crud.get_financial_profile(db, current_user.UserID)
    surplus = profile.MonthlySurplus if profile else 0
    if surplus <= 0: surplus = 100 # Fallback surplus if none
    
    # Sort for Snowball (Lowest Balance First)
    snowball_loans = sorted(loans, key=lambda x: x.OutstandingAmount)
    
    # Sort for Avalanche (Highest Interest First)
    avalanche_loans = sorted(loans, key=lambda x: x.InterestRate, reverse=True)
    
    def simulate_payoff(sorted_loans, extra_payment):
        # Extremely simplified simulation for demonstration
        months = 0
        total_interest_paid = 0
        remaining_balances = {l.LoanID: l.OutstandingAmount for l in sorted_loans}
        
        while any(b > 0 for b in remaining_balances.values()) and months < 360:
            months += 1
            available_cash = extra_payment
            
            # Pay minimums first
            for l in sorted_loans:
                if remaining_balances[l.LoanID] > 0:
                    interest = remaining_balances[l.LoanID] * (l.InterestRate / 100 / 12)
                    total_interest_paid += interest
                    remaining_balances[l.LoanID] += interest
                    
                    min_pay = min(l.EMI, remaining_balances[l.LoanID])
                    remaining_balances[l.LoanID] -= min_pay
            
            # Apply surplus to the targeted loan
            for l in sorted_loans:
                if remaining_balances[l.LoanID] > 0:
                    pay = min(available_cash, remaining_balances[l.LoanID])
                    remaining_balances[l.LoanID] -= pay
                    available_cash -= pay
                    if available_cash <= 0:
                        break
        
        return {"months": months, "total_interest_paid": round(total_interest_paid, 2)}
    
    snowball_res = simulate_payoff(snowball_loans, surplus)
    avalanche_res = simulate_payoff(avalanche_loans, surplus)
    
    return {
        "surplus_used": surplus,
        "snowball": snowball_res,
        "avalanche": avalanche_res
    }

# --------------------------
# Admin Panel
# --------------------------
@router.get("/admin/stats")
async def get_admin_stats(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.Email != "admin@example.com":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    users = db.query(models.User).all()
    loans = db.query(models.Loan).all()
    
    total_debt = sum(l.OutstandingAmount or 0 for l in loans)
    
    return {
        "total_users": len(users),
        "total_loans": len(loans),
        "total_system_debt": total_debt
    }

@router.get("/negotiations")
async def get_negotiations(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    negotiations = crud.get_user_negotiations(db, current_user.UserID)
    return negotiations

@router.get("/loans/{loan_id}/settlement-predictions")
async def get_loan_predictions(loan_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    loan = crud.get_loan_by_id(db, loan_id, current_user.UserID)
    return crud.get_loan_settlement_predictions(db, loan.LoanID)

@router.get("/ai-history")
async def get_ai_history(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.get_user_ai_history(db, current_user.UserID)
