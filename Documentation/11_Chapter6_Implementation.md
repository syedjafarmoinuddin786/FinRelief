# Chapter 6 — Implementation

This chapter describes the implementation details of the core modules of the **FinRelief AI** platform. It details the purpose, files, workflow, classes, algorithms, and database queries for each module.

---

## 6.1 Authentication Module

### Purpose
To secure user financial records and prevent unauthorized users from viewing portfolios or accessing AI APIs. It utilizes JWT-based session state.

### Implementation Details
* **Files Used**:
  * Backend: [auth.py](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/backend/app/routers/auth.py), [dependencies.py](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/backend/app/auth/dependencies.py), [security.py](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/backend/app/auth/security.py), [user_service.py](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/backend/app/services/user_service.py)
  * Frontend: [AuthContext.jsx](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/frontend/src/context/AuthContext.jsx), [api.js](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/frontend/src/services/api.js), [Login.jsx](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/frontend/src/pages/Login.jsx), [Register.jsx](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/frontend/src/pages/Register.jsx)
* **API Endpoints**:
  * `POST /api/v1/auth/register`: Receives registration schema, hashes the password using `verify_password` / `get_password_hash` with `pwd_context`, writes a new `User` entity to the database, and returns the profile.
  * `POST /api/v1/auth/login/json`: Receives JSON login inputs, checks credentials, issues a JWT token containing the `sub` claim (user ID), signed with a HS256 secret.
  * `GET /api/v1/auth/me`: Decodes the token using FastAPI dependency `Depends(get_current_user)` and returns the current user profile.
* **Authentication Flow**:
  1. Frontend submits credentials, receives JWT access token, and stores it in `localStorage.setItem('token', token)`.
  2. Axios interceptors inject the token into subsequent requests: `config.headers['Authorization'] = 'Bearer ' + token`.
  3. If a request returns `401 Unauthorized`, the interceptor clears the local token and redirects the browser to `/login`.
* **Screen Reference**: `01_login_page.png` (displays register and login panels).

---

## 6.2 Loan Portfolio CRUD Module

### Purpose
Allows users to maintain an active record of all their outstanding loans, EMIs, interest rates, and overdue periods.

### Implementation Details
* **Files Used**:
  * Backend: [loans.py](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/backend/app/routers/loans.py), [loan.py](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/backend/app/models/loan.py), [loan_service.py](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/backend/app/services/loan_service.py)
  * Frontend: [LoanManagement.jsx](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/frontend/src/pages/LoanManagement.jsx), [AddLoan.jsx](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/frontend/src/pages/AddLoan.jsx), [EditLoan.jsx](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/frontend/src/pages/EditLoan.jsx)
* **API Endpoints**:
  * `GET /api/v1/loans`: List all loans matching current authenticated user ID.
  * `POST /api/v1/loans`: Add a new loan record.
  * `GET /api/v1/loans/{loan_id}`: View specific loan details.
  * `PUT /api/v1/loans/{loan_id}`: Modify a loan's records.
  * `DELETE /api/v1/loans/{loan_id}`: Remove a loan.
* **Workflow**:
  Adding or modifying a loan updates the list, which triggers a request to `compute_full_financial_profile` to recalculate ratios (e.g. debt balances and EMI aggregates) and updates the dashboard.
* **Screen Reference**: `03_loan_crud.png` (displays the list of loans, amounts, interest rates, and overdue periods).

---

## 6.3 Financial Calculation Engine

### Purpose
Calculates DTI ratios, EMI ratios, and surplus cash to output a clear Financial Health Score and Stress Level.

### Implementation Details
* **Files Used**:
  * Backend: [financial.py](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/backend/app/routers/financial.py), [financial_profile.py](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/backend/app/models/financial_profile.py), [financial_engine.py](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/backend/app/services/financial_engine.py)
  * Frontend: [BudgetTracker.jsx](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/frontend/src/pages/BudgetTracker.jsx), [Profile.jsx](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/frontend/src/pages/Profile.jsx), [Dashboard.jsx](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/frontend/src/pages/Dashboard.jsx)
* **Mathematical Algorithms**:
  * **EMI Ratio Calculation**:
    $$\text{EMI Ratio} = \left( \frac{\text{Total EMIs}}{\text{Monthly Income}} \right) \times 100$$
  * **Debt-to-Income (DTI) Ratio**:
    $$\text{DTI Ratio} = \left( \frac{\text{Total Outstanding Debt}}{\text{Monthly Income} \times 12} \right) \times 100$$
  * **Health Score Calculation**:
    Starts at 100. Penalties are applied:
    * If EMI Ratio $> 50$, deduct $35$; $> 40$, deduct $25$; $> 30$, deduct $15$; $> 20$, deduct $5$.
    * If DTI $> 80$, deduct $30$; $> 60$, deduct $20$; $> 40$, deduct $10$; $> 30$, deduct $5$.
    * If surplus cash is negative, deduct $25$; if surplus ratio is $< 5\%$, deduct $15$; $< 10\%$, deduct $10$; $< 20\%$, deduct $5$.
    * Final score restricted between 0.0 and 100.0.
  * **Stress Level Classification**:
    * Score $\ge 70$: **Low**
    * Score $\ge 50$: **Medium**
    * Score $\ge 30$: **High**
    * Score $< 30$: **Critical**
* **Database Interactions**:
  Calculated profiles are written to the `financial_profiles` table to maintain the state of the user dashboard.
* **Screen Reference**: `02_dashboard_overview.png` (displays surplus, health score out of 100, DTI, and stress level).

---

## 6.4 Settlement Prediction Engine

### Purpose
Calculates recommended settlement targets and prioritizes creditor negotiations.

### Implementation Details
* **Files Used**:
  * Backend: [settlement.py](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/backend/app/routers/settlement.py), [settlement_record.py](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/backend/app/models/settlement_record.py), [settlement_engine.py](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/backend/app/services/settlement_engine.py)
  * Frontend: [SettlementPredictor.jsx](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/frontend/src/pages/SettlementPredictor.jsx)
* **Strategic Algorithms**:
  * **Base Settlement Percentage**:
    Starts at 70%. Adjustments are applied:
    * **Loan Type**: Credit Card $-15\%$; Personal $-10\%$; Business $-8\%$; Auto $-5\%$; Student $-3\%$; Home $0\%$.
    * **Interest Rate**: $>30\%$, deduct $10\%$; $>20\%$, deduct $7\%$; $>15\%$, deduct $4\%$.
    * **Overdue Duration**: $>24$ months, deduct $15\%$; $>12$ months, deduct $10\%$; $>6$ months, deduct $5\%$; $>3$ months, deduct $2\%$.
    * Output is capped between 30% and 90%.
  * **Priority Score**:
    * If overdue months $> 12$ or DTI $> 60\%$: **Critical**.
    * If overdue months $> 6$ or DTI $> 40\%$: **High**.
    * If overdue months $> 3$ or DTI $> 25\%$: **Medium**.
    * Otherwise: **Low**.
  * **Risk Category**:
    Score compiled based on overdue months ($>12: 3$ pts, $>6: 2$ pts, $>3: 1$ pt), interest rates ($>25\%: 2$ pts, $>15\%: 1$ pt), and outstanding-to-original ratio ($>80\%: 2$ pts, $>50\%: 1$ pt).
    * Points $\ge 6$: **Critical**.
    * Points $\ge 4$: **High**.
    * Points $\ge 2$: **Moderate**.
    * Otherwise: **Low**.
* **Database Interactions**:
  Calculations are saved to the `settlement_records` table to display past predictions.
* **Screen Reference**: `04_settlement_predictions.png` (displays recommended targets, risk levels, and priorities).

---

## 6.5 AI Core & Fallback Orchestration

### Purpose
Orchestrates requests to the Google Gemini API, falling back to local rule-based models when the API is unconfigured or offline.

### Implementation Details
* **Files Used**:
  * Backend: [ai.py](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/backend/app/routers/ai.py), [ai_orchestrator.py](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/backend/app/services/ai_orchestrator.py), [gemini_service.py](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/backend/app/services/gemini_service.py), [fallback_engine.py](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/backend/app/services/fallback_engine.py)
* **Workflow**:
  1. The API receives a request to generate a strategy or letter.
  2. `GeminiService` verifies configuration availability.
  3. If `settings.GEMINI_API_KEY` is present and active, the prompt is sent to `gemini-pro`.
  4. If an exception is raised, the `ai_orchestrator` catches the error, calls `fallback_engine`, sets `is_fallback = True`, and returns the output to the client.
* **Screen Reference**: `05_ai_negotiation_letter.png` (displays the generated letter text and indicates if fallback was used).

---

## 6.6 AI History & Counselor Chat Logs

### Purpose
Saves generated letters and counselors logs to the database, supporting pagination to prevent memory bloat.

### Implementation Details
* **Files Used**:
  * Backend: [history.py](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/backend/app/routers/history.py), [ai_history.py](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/backend/app/models/ai_history.py)
  * Frontend: [AIHistory.jsx](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/frontend/src/pages/AIHistory.jsx)
* **Database Interactions**:
  Every generated response is saved to the `ai_history` table:
  ```python
  record = AIHistory(
      user_id=user_id,
      request_type=request_type,
      prompt_summary=prompt_summary,
      response_text=response_text,
      model_used=model_used,
      is_fallback=is_fallback
  )
  db.add(record)
  db.commit()
  ```
  Retrieval endpoints support pagination:
  ```python
  records = query.offset(skip).limit(limit).all()
  ```
* **Screen Reference**: The AI History page displays cards showing all previously generated hardship letters and counselor logs.
