import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("Testing POST /api/analyze-debt...")
response = client.post("/api/analyze-debt", json={
    "total_debt": 15000.0,
    "monthly_income": 4000.0,
    "monthly_expenses": 3200.0
})

print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    print("Success! Advice received:")
    print(response.json().get("advice"))
else:
    print("Error details:")
    print(response.json())
