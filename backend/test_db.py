import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.db import crud, models
from app.db.database import SessionLocal, engine

# Ensure tables are created
models.Base.metadata.create_all(bind=engine)

def test_db():
    db = SessionLocal()
    try:
        # 1. Create a User
        user = crud.create_user(
            db=db,
            name="Test User",
            email="test@finrelief.com",
            password="securepassword123",
            income=5000.0,
            expenses=2000.0
        )
        print(f"Created User: {user.Name} (ID: {user.UserID})")
        
        # 2. Create a Financial Profile for the User
        profile = crud.create_or_update_financial_profile(
            db=db,
            user_id=user.UserID,
            emi_ratio=0.3,
            dti_ratio=0.4,
            monthly_surplus=1500.0,
            stress_level="Medium"
        )
        print(f"Created Financial Profile: Surplus ${profile.MonthlySurplus} for User ID {profile.UserID}")

        # 3. Create a Loan for the User
        loan = crud.create_loan(
            db=db,
            user_id=user.UserID,
            lender_name="Bank of Tech",
            loan_type="Personal",
            outstanding_amount=10000.0,
            interest_rate=12.5,
            emi=350.0,
            overdue_months=1
        )
        print(f"Created Loan: {loan.LenderName} for User ID {loan.UserID}")

        # 4. Verify Read Operations
        fetched_user = crud.get_user_by_email(db, "test@finrelief.com")
        print(f"Fetched User: {fetched_user.Name}, Password Match: {crud.verify_password('securepassword123', fetched_user.Password)}")
        
        user_loans = crud.get_loans_by_user(db, fetched_user.UserID)
        print(f"User has {len(user_loans)} loan(s).")
        
    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_db()
