# Chapter 7 — Testing

This chapter describes the testing strategy, test cases, bug fixes, validation, and error handling mechanisms implemented for the **FinRelief AI** platform.

---

## 7.1 Testing Strategy
The testing strategy combines automated endpoint testing and manual user-interface walkthroughs:
1. **Unit Testing**: Testing individual services (e.g. `financial_engine.py` math and `fallback_engine.py` responses) to ensure correct calculations.
2. **Integration Testing**: Verifying database operations and route security (e.g. checking that endpoints reject requests missing a JWT header).
3. **System Testing**: Validating complete user flows (e.g. registering a new user, adding three active loans, updating budget metrics, predicting settlement targets, and drafting a hardship letter).
4. **Validation Testing**: Confirming that input validation catches malformed requests (e.g., negative incomes or invalid email formats).

---

## 7.2 System Test Cases

| Test ID | Test Category | Description | Input Data | Expected Output | Actual Output | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-01** | Authentication | Register new user | Email: `test@user.com`, Password: `secure123`, Name: `Test User` | HTTP 201; JSON success response; password encrypted in DB. | HTTP 201; user created; password hashed. | **Passed** |
| **TC-02** | Authentication | Reject duplicate registration | Register same email twice | HTTP 400 Bad Request; message "A user with this email already exists." | HTTP 400 Bad Request; error returned. | **Passed** |
| **TC-03** | Authentication | Attempt access to protected routes without JWT | Request `GET /api/v1/loans` without token | HTTP 401 Unauthorized; header challenge present. | HTTP 401 Unauthorized; access blocked. | **Passed** |
| **TC-04** | Financial Engine | Calculate financial health with positive surplus | Income: `10,000`, Expenses: `4,000`, Loan EMI: `2,000` | Surplus: `4,000`, EMI Ratio: `20%`, Stress Level: `Low`, Score: `95.0`. | Surplus: `4,000.00`, EMI Ratio: `20.00%`, Stress: `Low`, Score: `95.00`. | **Passed** |
| **TC-05** | Financial Engine | Calculate financial health with negative surplus | Income: `5,000`, Expenses: `4,000`, Loan EMI: `2,000` | Surplus: `-1,000`, EMI Ratio: `40%`, Stress: `Critical` / `High` (Score penalized). | Surplus: `-1,000.00`, EMI Ratio: `40.00%`, Stress: `Critical`, Score: `20.00`. | **Passed** |
| **TC-06** | Settlement Engine | Predict settlement for overdue credit card loan | CC Loan, Outstanding: `10,000`, Rate: `32%`, Overdue: `13` months | Recommended payout target ~40-50%; priority: Critical; risk: Critical. | Recommended percentage: `40%`, target: `₹4,000`, Priority: `Critical`. | **Passed** |
| **TC-07** | AI & Fallback | Generate letter with missing Gemini API key | Letter generation request, empty key | Core system redirects to fallback; returns rule-based template; `is_fallback = True`. | Letter generated; `is_fallback = True`, model: `fallback`. | **Passed** |

---

## 7.3 Bug Fixes

### 1. SQLite Database Write-Locks (OneDrive Synced Folders)
* **Problem**: When run in synced local folders like OneDrive, SQLite encountered database write-locks (`sqlite3.OperationalError: database is locked`) because OneDrive locked the SQLite WAL/SHM temp files.
* **Fix**:
  1. Set connection timeout parameters: `connect_args = {"check_same_thread": False, "timeout": 30}` to retry locks.
  2. Changed SQLite database journaling mode to `DELETE` and synchronization to `NORMAL` in [database.py](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/backend/app/database.py#L33-L42). This stops SQLite from generating external WAL temp files, avoiding sync locks.

### 2. Relative Path Mismatches
* **Problem**: Launching the backend server from different terminal directories caused SQLite to create separate empty databases, as relative URLs (like `sqlite:///./finrelief.db`) resolved differently based on the terminal's working directory.
* **Fix**: Added dynamic resolution logic in [database.py](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/backend/app/database.py#L11-L19) to convert relative paths into absolute paths based on the backend folder root.

---

## 7.4 Validation & Error Handling

* **Pydantic Validation (HTTP 422)**:
  If a user submits an invalid request (such as letters in a numeric interest rate field), Pydantic catches the validation error. The custom exception handler in [main.py](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/backend/app/main.py#L75-L88) returns a standardized error response:
  ```json
  {
    "success": false,
    "message": "Validation Error",
    "error": {
      "code": 422,
      "details": [...]
    }
  }
  ```
* **JWT Expiry Handling**:
  If a token is expired, the decoding helper throws a `JWTError`. The backend rejects the request with `HTTP 401 Unauthorized`, prompting the frontend to redirect the user to `/login`.
