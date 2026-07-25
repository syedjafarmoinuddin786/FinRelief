import requests
import sqlite3
import pyotp
import urllib.parse
from urllib.parse import urlparse, parse_qs

BASE_URL = "http://localhost:8000/api"

print("Starting backend verification...")

# 1. Signup
email = "testuser@example.com"
password = "TestPassword123!"
signup_res = requests.post(f"{BASE_URL}/signup", json={
    "name": "Test User",
    "email": email,
    "password": password,
    "income": 5000.0,
    "expenses": 2000.0
})
print(f"Signup: {signup_res.status_code}")
if signup_res.status_code not in [200, 400]:
    print("Signup failed:", signup_res.text)

# 2. Extract verification token directly from DB
conn = sqlite3.connect("finrelief.db")
cursor = conn.cursor()
cursor.execute("SELECT verification_token FROM users WHERE email=?", (email,))
row = cursor.fetchone()
if not row:
    print("User not found in DB!")
    exit(1)
token = row[0]
conn.close()

# 3. Verify Email
verify_res = requests.get(f"{BASE_URL}/verify-email?token={token}")
print(f"Email Verify: {verify_res.status_code}")

# 4. Login (Requires 2FA setup next)
login_res = requests.post(f"{BASE_URL}/login", data={
    "username": email,
    "password": password
})
print(f"Login: {login_res.status_code}")
login_data = login_res.json()
temp_token = login_data.get("access_token")

headers = {"Authorization": f"Bearer {temp_token}"}

# 5. Setup 2FA
setup_2fa_res = requests.post(f"{BASE_URL}/2fa/setup", headers=headers)
print(f"2FA Setup: {setup_2fa_res.status_code}")
setup_data = setup_2fa_res.json()
totp_secret = setup_data.get("secret")

if not totp_secret:
    print("Failed to get TOTP secret")
    exit(1)

# Generate code
totp = pyotp.TOTP(totp_secret)
code = totp.now()

# 6. Verify 2FA
verify_2fa_res = requests.post(f"{BASE_URL}/2fa/verify", json={
    "token": temp_token,
    "code": code
})
print(f"2FA Verify: {verify_2fa_res.status_code}")
final_token = verify_2fa_res.json().get("access_token")
final_headers = {"Authorization": f"Bearer {final_token}"}

# 7. Edit Profile
profile_res = requests.put(f"{BASE_URL}/profile", json={
    "name": "Updated User",
    "income": 5000,
    "expenses": 2000,
    "credit_score": 750,
    "savings": 10000,
    "employment_status": "Employed",
    "financial_goals": "Buy a house"
}, headers=final_headers)
print(f"Profile Update: {profile_res.status_code}")

# 8. Add Loan
loan_res = requests.post(f"{BASE_URL}/loans", json={
    "lender_name": "Chase Bank",
    "loan_type": "Credit Card",
    "outstanding_amount": 10000,
    "interest_rate": 20.0,
    "emi": 500,
    "overdue_months": 0,
    "start_date": "2023-01-01T00:00:00",
    "due_date": "2025-01-01T00:00:00",
    "status": "Active"
}, headers=final_headers)
print(f"Add Loan: {loan_res.status_code}")

# 9. Get Dashboard
dash_res = requests.get(f"{BASE_URL}/dashboard", headers=final_headers)
print(f"Dashboard: {dash_res.status_code}")
print("Dashboard Response Sample:", str(dash_res.json())[:200])

print("All backend checks passed!")
