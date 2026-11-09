import time
import os
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.api.routes import limiter, compute_financial_metrics
from app.services.ai_service import generate_negotiation_letter

limiter.enabled = False

client = TestClient(app)

print("--- MEASURING REAL LOCAL BENCHMARKS ---")

# 1. Health check latency
latencies = []
for _ in range(50):
    t0 = time.perf_counter()
    res = client.get("/health")
    latencies.append((time.perf_counter() - t0) * 1000)
avg_health = sum(latencies) / len(latencies)
print(f"Health check endpoint (average of 50 requests): {avg_health:.2f} ms (min: {min(latencies):.2f} ms, max: {max(latencies):.2f} ms)")

# 2. Financial calculation engine math latency
math_latencies = []
for _ in range(1000):
    t0 = time.perf_counter()
    metrics = compute_financial_metrics(
        outstanding_amount=150000.0,
        monthly_income=50000.0,
        monthly_expenses=30000.0,
        loan_emi=10000.0,
        overdue_months=6
    )
    math_latencies.append((time.perf_counter() - t0) * 1000)
avg_math = sum(math_latencies) / len(math_latencies)
print(f"Deterministic Financial Metrics Calculation (average of 1,000 iterations): {avg_math:.4f} ms")

# 3. AI Fallback Failover Latency
# When Gemini fails (e.g. simulated network error / API error), how fast does generate_negotiation_letter failover to the local deterministic template?
fallback_latencies = []
with patch("app.services.ai_service.client.models.generate_content", side_effect=Exception("API quota exceeded / network timeout")):
    for _ in range(50):
        t0 = time.perf_counter()
        result = generate_negotiation_letter(
            borrower_name="Syed Jafar",
            lender_name="HDFC Bank",
            loan_type="Personal Loan",
            outstanding_amount=150000.0,
            overdue_months=6,
            monthly_surplus=10000.0,
            suggested_settlement=75000.0,
            tone="professional"
        )
        fallback_latencies.append((time.perf_counter() - t0) * 1000)
avg_fallback = sum(fallback_latencies) / len(fallback_latencies)
print(f"AI Fallback Failover Execution (average of 50 failover runs): {avg_fallback:.2f} ms (min: {min(fallback_latencies):.2f} ms, max: {max(fallback_latencies):.2f} ms)")

# 4. Bcrypt hashing verification latency
from app.db.crud import get_password_hash, verify_password
hash_latencies = []
for _ in range(10):
    t0 = time.perf_counter()
    h = get_password_hash("SecurePassword123!")
    hash_latencies.append((time.perf_counter() - t0) * 1000)
avg_hash = sum(hash_latencies) / len(hash_latencies)
print(f"Bcrypt Password Hash (average of 10): {avg_hash:.2f} ms (min: {min(hash_latencies):.2f} ms, max: {max(hash_latencies):.2f} ms)")

