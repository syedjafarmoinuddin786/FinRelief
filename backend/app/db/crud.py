from sqlalchemy.orm import Session
import bcrypt
import secrets
from . import models
from fastapi import HTTPException

# --------------------------
# Authentication / Passwords (A04)
# --------------------------
def get_password_hash(password: str) -> str:
    # Hash password using bcrypt directly
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_bytes.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except ValueError:
        return False

# --------------------------
# CRUD: Users
# --------------------------
def create_user(db: Session, name: str, email: str, password: str, income: float, expenses: float) -> models.User:
    hashed_password = get_password_hash(password)
    verification_token = secrets.token_urlsafe(32)
    db_user = models.User(
        Name=name,
        Email=email.lower().strip(),
        Password=hashed_password,
        MonthlyIncome=income,
        MonthlyExpenses=expenses,
        verification_token=verification_token,
        is_verified=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_verification_token(db: Session, token: str) -> models.User | None:
    return db.query(models.User).filter(models.User.verification_token == token).first()

def verify_email(db: Session, user: models.User) -> models.User:
    user.is_verified = True
    user.verification_token = None
    db.commit()
    db.refresh(user)
    return user

def set_reset_token(db: Session, user: models.User) -> str:
    token = "".join([str(secrets.randbelow(10)) for _ in range(6)])
    user.reset_token = token
    db.commit()
    return token

def get_user_by_reset_token(db: Session, email: str, token: str) -> models.User | None:
    return db.query(models.User).filter(
        models.User.Email == email.lower().strip(),
        models.User.reset_token == token
    ).first()

def reset_password(db: Session, user: models.User, new_password: str) -> models.User:
    user.Password = get_password_hash(new_password)
    user.reset_token = None
    db.commit()
    return user

def set_totp_secret(db: Session, user: models.User, secret: str) -> models.User:
    user.totp_secret = secret
    db.commit()
    db.refresh(user)
    return user

def enable_2fa(db: Session, user: models.User) -> models.User:
    user.is_2fa_enabled = True
    db.commit()
    db.refresh(user)
    return user

def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.query(models.User).filter(models.User.Email == email.lower().strip()).first()

def get_user_by_id(db: Session, user_id: int) -> models.User | None:
    return db.query(models.User).filter(models.User.UserID == user_id).first()

def update_user_profile(db: Session, user: models.User, update_data: dict) -> models.User:
    for key, value in update_data.items():
        if value is not None:
            if key == "name": user.Name = value
            elif key == "income": user.MonthlyIncome = value
            elif key == "expenses": user.MonthlyExpenses = value
            elif key == "credit_score": user.CreditScore = value
            elif key == "savings": user.Savings = value
            elif key == "employment_status": user.EmploymentStatus = value
            elif key == "financial_goals": user.FinancialGoals = value
    db.commit()
    db.refresh(user)
    return user

def update_user_password(db: Session, user: models.User, new_password: str) -> models.User:
    user.Password = get_password_hash(new_password)
    db.commit()
    return user

# --------------------------
# CRUD: Financial Profile
# --------------------------
def upsert_financial_profile(
    db: Session, user_id: int, emi_ratio: float, dti_ratio: float, 
    monthly_surplus: float, stress_level: str
) -> models.FinancialProfile:
    db_profile = db.query(models.FinancialProfile).filter(models.FinancialProfile.UserID == user_id).first()
    
    if db_profile:
        db_profile.EMI_Ratio = emi_ratio
        db_profile.DTI_Ratio = dti_ratio
        db_profile.MonthlySurplus = monthly_surplus
        db_profile.StressLevel = stress_level
    else:
        db_profile = models.FinancialProfile(
            UserID=user_id,
            EMI_Ratio=emi_ratio,
            DTI_Ratio=dti_ratio,
            MonthlySurplus=monthly_surplus,
            StressLevel=stress_level
        )
        db.add(db_profile)
    
    db.commit()
    db.refresh(db_profile)
    return db_profile

def get_financial_profile(db: Session, user_id: int) -> models.FinancialProfile | None:
    return db.query(models.FinancialProfile).filter(models.FinancialProfile.UserID == user_id).first()

# --------------------------
# CRUD: Loans (A01 - ownership validation)
# --------------------------
def create_loan(
    db: Session, user_id: int, lender_name: str, loan_type: str, 
    outstanding_amount: float, interest_rate: float, emi: float, overdue_months: int,
    start_date = None, due_date = None, status: str = "Active"
) -> models.Loan:
    db_loan = models.Loan(
        UserID=user_id,
        LenderName=lender_name,
        LoanType=loan_type,
        OutstandingAmount=outstanding_amount,
        InterestRate=interest_rate,
        EMI=emi,
        OverdueMonths=overdue_months,
        StartDate=start_date,
        DueDate=due_date,
        Status=status
    )
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    return db_loan

def get_user_loans(db: Session, user_id: int) -> list[models.Loan]:
    return db.query(models.Loan).filter(models.Loan.UserID == user_id).all()

def get_loan_by_id(db: Session, loan_id: int, user_id: int) -> models.Loan:
    # A01: Verify record belongs to current_user. Return 404 if not found or not owned.
    loan = db.query(models.Loan).filter(models.Loan.LoanID == loan_id).first()
    if not loan or loan.UserID != user_id:
        raise HTTPException(status_code=404, detail="Loan not found")
    return loan

def update_loan(db: Session, loan: models.Loan, update_data: dict) -> models.Loan:
    mapping = {
        "lender_name": "LenderName",
        "loan_type": "LoanType",
        "outstanding_amount": "OutstandingAmount",
        "interest_rate": "InterestRate",
        "emi": "EMI",
        "overdue_months": "OverdueMonths",
        "start_date": "StartDate",
        "due_date": "DueDate",
        "status": "Status"
    }
    for key, value in update_data.items():
        if key in mapping and value is not None:
            setattr(loan, mapping[key], value)
    db.commit()
    db.refresh(loan)
    return loan

def delete_loan(db: Session, loan: models.Loan):
    db.delete(loan)
    db.commit()

# --------------------------
# CRUD: Settlement Predictions
# --------------------------
def create_settlement_prediction(
    db: Session, loan_id: int, suggested_settlement: float, 
    risk_category: str, predicted_amount: float
) -> models.SettlementPrediction:
    prediction = models.SettlementPrediction(
        LoanID=loan_id,
        SuggestedSettlement=suggested_settlement,
        RiskCategory=risk_category,
        PredictedAmount=predicted_amount
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction

def get_loan_settlement_predictions(db: Session, loan_id: int) -> list[models.SettlementPrediction]:
    return db.query(models.SettlementPrediction).filter(models.SettlementPrediction.LoanID == loan_id).order_by(models.SettlementPrediction.SettlementID.desc()).all()

# --------------------------
# CRUD: AI History
# --------------------------
def create_ai_history(db: Session, user_id: int, content: str, query_type: str) -> models.AIHistory:
    history = models.AIHistory(
        UserID=user_id,
        GeneratedContent=content,
        QueryType=query_type
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    return history

def get_user_ai_history(db: Session, user_id: int) -> list[models.AIHistory]:
    return db.query(models.AIHistory).filter(models.AIHistory.UserID == user_id).order_by(models.AIHistory.Timestamp.desc()).all()

# --------------------------
# CRUD: AI Negotiations
# --------------------------
def create_ai_negotiation(
    db: Session, user_id: int, loan_id: int, strategy: str, letter: str
) -> models.AINegotiation:
    negotiation = models.AINegotiation(
        UserID=user_id,
        LoanID=loan_id,
        NegotiationStrategy=strategy,
        NegotiationLetter=letter
    )
    db.add(negotiation)
    db.commit()
    db.refresh(negotiation)
    return negotiation

def get_user_negotiations(db: Session, user_id: int) -> list[models.AINegotiation]:
    return db.query(models.AINegotiation).filter(models.AINegotiation.UserID == user_id).order_by(models.AINegotiation.GeneratedDate.desc()).all()

# --------------------------
# CRUD: Settings
# --------------------------
def get_user_settings(db: Session, user_id: int) -> models.Setting:
    setting = db.query(models.Setting).filter(models.Setting.UserID == user_id).first()
    if not setting:
        setting = models.Setting(UserID=user_id)
        db.add(setting)
        db.commit()
        db.refresh(setting)
    return setting

def update_user_settings(db: Session, setting: models.Setting, theme: str, currency: str, language: str, notif_enabled: bool) -> models.Setting:
    setting.Theme = theme
    setting.Currency = currency
    setting.Language = language
    setting.NotificationsEnabled = notif_enabled
    db.commit()
    db.refresh(setting)
    return setting
