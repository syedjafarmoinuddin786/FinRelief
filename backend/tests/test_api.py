import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
from unittest.mock import patch
from app.main import app
from app.db.database import get_db, Base
from app.db import models
from app.core import security

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user_token():
    response = client.post("/api/signup", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "Password123!",
        "income": 5000.0,
        "expenses": 3000.0
    })
    return response.json()["access_token"]

@pytest.fixture
def other_user_token():
    response = client.post("/api/signup", json={
        "name": "Other User",
        "email": "other@example.com",
        "password": "Password123!",
        "income": 4000.0,
        "expenses": 2000.0
    })
    return response.json()["access_token"]

# --------------------------
# Authentication Tests (A06: Weak Passwords)
# --------------------------
def test_signup_success():
    response = client.post("/api/signup", json={
        "name": "New User",
        "email": "new@example.com",
        "password": "Password123!",
        "income": 5000,
        "expenses": 3000
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_signup_weak_password():
    # A06: Password length < 8 should fail Pydantic validation
    response = client.post("/api/signup", json={
        "name": "Weak User",
        "email": "weak@example.com",
        "password": "weak",
        "income": 5000,
        "expenses": 3000
    })
    assert response.status_code == 422 # Unprocessable Entity

def test_login_success(test_user_token):
    response = client.post("/api/login", data={
        "username": "test@example.com",
        "password": "Password123!"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

# --------------------------
# Loan CRUD & Ownership Tests (A01)
# --------------------------
def test_create_loan(test_user_token):
    response = client.post("/api/loans", json={
        "lender_name": "Bank A",
        "loan_type": "Credit Card",
        "outstanding_amount": 10000,
        "interest_rate": 18.0,
        "emi": 300,
        "overdue_months": 0
    }, headers={"Authorization": f"Bearer {test_user_token}"})
    assert response.status_code == 200
    assert response.json()["LoanID"] is not None

def test_get_loan_ownership_protection(test_user_token, other_user_token):
    # 1. Test user creates a loan
    loan_response = client.post("/api/loans", json={
        "lender_name": "Bank A",
        "loan_type": "Credit Card",
        "outstanding_amount": 10000,
        "interest_rate": 18.0,
        "emi": 300,
        "overdue_months": 0
    }, headers={"Authorization": f"Bearer {test_user_token}"})
    loan_id = loan_response.json()["LoanID"]

    # 2. Other user tries to access the loan
    # A01: Must return 404
    attack_response = client.get(f"/api/loans/{loan_id}", headers={"Authorization": f"Bearer {other_user_token}"})
    assert attack_response.status_code == 404

# --------------------------
# AI Endpoints with Mocks
# --------------------------
@patch("app.services.ai_service.client.models.generate_content")
def test_settlement_recommendation(mock_generate, test_user_token):
    # Mock Gemini response
    mock_generate.return_value.text = "## Debt Stress Analysis\nHigh stress.\n\n## Financial Health Insights\nDTI is bad.\n\n## Settlement Recommendation\nSettle for this amount."
    
    # Setup Loan
    loan_response = client.post("/api/loans", json={
        "lender_name": "Bank A", "loan_type": "Credit Card",
        "outstanding_amount": 10000, "interest_rate": 18.0,
        "emi": 300, "overdue_months": 0
    }, headers={"Authorization": f"Bearer {test_user_token}"})
    loan_id = loan_response.json()["LoanID"]

    # Test Settlement Endpoint
    response = client.post(f"/api/loans/{loan_id}/settlement-recommendation", headers={"Authorization": f"Bearer {test_user_token}"})
    assert response.status_code == 200
    data = response.json()
    assert "suggested_settlement" in data
    assert "narrative" in data
    assert data["stress_level"] == "Low" # based on the formula with EMI 300 / 5000 = 0.06

@patch("app.services.ai_service.client.models.generate_content")
def test_negotiation_letter(mock_generate, test_user_token):
    mock_generate.return_value.text = "## Strategy\nWe negotiate hard.\n## Letter\nDear Bank,\nLet's settle.\nSincerely, Me."
    
    loan_response = client.post("/api/loans", json={
        "lender_name": "Bank A", "loan_type": "Credit Card",
        "outstanding_amount": 10000, "interest_rate": 18.0,
        "emi": 300, "overdue_months": 0
    }, headers={"Authorization": f"Bearer {test_user_token}"})
    loan_id = loan_response.json()["LoanID"]

    response = client.post(f"/api/loans/{loan_id}/negotiation-letter", json={"tone": "professional"}, headers={"Authorization": f"Bearer {test_user_token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["strategy"] == "We negotiate hard."
    assert "Dear Bank," in data["letter"]
