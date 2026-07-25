import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
from app.db.database import Base, engine, SessionLocal
from app.models import models

# Mocking Gemini
@pytest.fixture(autouse=True)
def mock_gemini():
    with patch("app.services.ai_service.client.models.generate_content") as mock_generate:
        mock_response = type("MockResponse", (), {"text": "## Strategy\nThis is a mocked strategy.\n## Letter\nThis is a mocked letter."})()
        mock_generate.return_value = mock_response
        yield mock_generate

@pytest.fixture(scope="module")
def client():
    # Setup fresh DB
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_signup_and_login(client):
    # Signup
    signup_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "securepassword123",
        "income": 5000.0,
        "expenses": 3000.0
    }
    response = client.post("/api/signup", json=signup_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    
    # Login
    login_data = {
        "username": "test@example.com",
        "password": "securepassword123"
    }
    response = client.post("/api/login", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_create_and_get_loan(client):
    # Login to get token
    login_data = {"username": "test@example.com", "password": "securepassword123"}
    token = client.post("/api/login", data=login_data).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create Loan
    loan_data = {
        "lender_name": "Chase Bank",
        "loan_type": "Credit Card",
        "outstanding_amount": 10000.0,
        "interest_rate": 20.0,
        "emi": 500.0,
        "overdue_months": 2
    }
    response = client.post("/api/loans", json=loan_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Loan added successfully"
    
    # Get Loans
    response = client.get("/api/loans", headers=headers)
    assert response.status_code == 200
    loans = response.json()["loans"]
    assert len(loans) == 1
    assert loans[0]["lender_name"] == "Chase Bank"
    
    return loans[0]["id"]

def test_settlement_recommendation(client):
    # Get token
    token = client.post("/api/login", data={"username": "test@example.com", "password": "securepassword123"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get the loan ID
    loans = client.get("/api/loans", headers=headers).json()["loans"]
    loan_id = loans[0]["id"]
    
    # Trigger settlement recommendation
    response = client.post(f"/api/loans/{loan_id}/settlement-recommendation", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "emi_ratio" in data
    assert "narrative" in data
    assert "mocked" in data["narrative"] or "## Strategy" in data["narrative"]

def test_negotiation_letter(client):
    # Get token
    token = client.post("/api/login", data={"username": "test@example.com", "password": "securepassword123"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get the loan ID
    loans = client.get("/api/loans", headers=headers).json()["loans"]
    loan_id = loans[0]["id"]
    
    # Trigger negotiation letter
    response = client.post(f"/api/loans/{loan_id}/negotiation-letter", json={"tone": "professional"}, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "strategy" in data
    assert "letter" in data
    assert "This is a mocked strategy" in data["strategy"]
    assert "This is a mocked letter" in data["letter"]

def test_unauthorized_access(client):
    response = client.get("/api/loans")
    assert response.status_code == 401
