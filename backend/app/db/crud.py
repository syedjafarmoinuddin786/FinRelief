from sqlalchemy.orm import Session
from passlib.context import CryptContext
from . import models

# Password Hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# --------------------------
# CRUD operations for Users
# --------------------------
def create_user(db: Session, name: str, email: str, password: str, income: float, expenses: float) -> models.User:
    hashed_password = get_password_hash(password)
    db_user = models.User(
        Name=name,
        Email=email,
        Password=hashed_password,
        MonthlyIncome=income,
        MonthlyExpenses=expenses
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.query(models.User).filter(models.User.Email == email).first()

def get_user_by_id(db: Session, user_id: int) -> models.User | None:
    return db.query(models.User).filter(models.User.UserID == user_id).first()

# --------------------------------------
# CRUD operations for Financial_Profile
# --------------------------------------
def create_or_update_financial_profile(
    db: Session, user_id: int, emi_ratio: float, dti_ratio: float, monthly_surplus: float, stress_level: str
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

# --------------------------
# CRUD operations for Loans
# --------------------------
def create_loan(
    db: Session, user_id: int, lender_name: str, loan_type: str, 
    outstanding_amount: float, interest_rate: float, emi: float, overdue_months: int
) -> models.Loan:
    db_loan = models.Loan(
        UserID=user_id,
        LenderName=lender_name,
        LoanType=loan_type,
        OutstandingAmount=outstanding_amount,
        InterestRate=interest_rate,
        EMI=emi,
        OverdueMonths=overdue_months
    )
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    return db_loan

def get_loans_by_user(db: Session, user_id: int) -> list[models.Loan]:
    return db.query(models.Loan).filter(models.Loan.UserID == user_id).all()
