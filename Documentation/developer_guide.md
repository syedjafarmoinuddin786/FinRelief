# Developer Setup & Architecture Guide

This guide describes the code structure, development patterns, and extension paths of the **FinRelief AI** platform.

---

## 1. System Architecture Details

The system separates concerns between the React SPA and the FastAPI Python gateway.

### 1.1 Backend Dependency Injection
FastAPI leverages dependency injection for database sessions and route protection. For example:
```python
@router.post("", response_model=ApiResponse[LoanResponse])
def create_loan(
    loan_in: LoanCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Route logic
```
* **`Depends(get_db)`**: Resolves database sessions, yielding a session context that is closed automatically after execution.
* **`Depends(get_current_user)`**: Extracts the JWT token, decodes the signature, verifies the user, and blocks the request if the token is invalid.

### 1.2 Database Migration Path
The system uses SQLite initialized directly on import via SQLAlchemy `Base.metadata.create_all(bind=engine)` in `main.py`. For production database schema updates, we recommend configuring Alembic:
```bash
pip install alembic
alembic init migrations
```
Configure `sqlalchemy.url` in `alembic.ini` to read environment variables, and update target tables in `migrations/env.py`.

---

## 2. Frontend Structure & Design Tokens

### 2.1 CSS Theme variables
Styling uses CSS variables in [index.css](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/frontend/src/styles/index.css) to enforce design consistency. Key variables include:
* Background: `--bg-main: #0B0F19;`
* Card surface: `--bg-surface: rgba(17, 24, 39, 0.7);`
* Glass background: `--glass-bg: rgba(20, 26, 46, 0.6);`
* Glow borders: `--border-glow: rgba(99, 102, 241, 0.25);`

### 2.2 Functional Route Protections
The frontend routes are protected using the `RequireAuth` wrapper in `App.jsx`:
```jsx
const RequireAuth = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  if (loading) return <div>Initializing Session...</div>;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return children;
};
```

---

## 3. Extending the Codebase

### 3.1 Adding a New Loan Type
To add a new loan type (e.g., `medical`):
1. **Pydantic Validation**: Update input constraints in [loan.py](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/backend/app/schemas/loan.py) if validation checks exist.
2. **Settlement Adjustments**: Update `type_adjustments` inside `_calculate_base_settlement_percentage` in [settlement_engine.py](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/backend/app/services/settlement_engine.py#L15-L22):
   ```python
   type_adjustments = {
       "credit_card": -15.0,
       "personal": -10.0,
       "medical": -12.0, # Add new entry
       ...
   }
   ```
3. **Frontend Display Map**: Add the display label to the `LOAN_TYPES` object in [Dashboard.jsx](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/frontend/src/pages/Dashboard.jsx#L22-L29), [AddLoan.jsx](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/frontend/src/pages/AddLoan.jsx), and [SettlementPredictor.jsx](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/frontend/src/pages/SettlementPredictor.jsx#L6-L13):
   ```javascript
   const LOAN_TYPES = {
     personal: 'Personal Loan',
     medical: 'Medical Loan', // Add new entry
     ...
   };
   ```

### 3.2 Modifying the Financial Health Penalties
To adjust how the Financial Health Score is calculated, update [financial_engine.py](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/backend/app/services/financial_engine.py#L32-L72). For example, to apply a harsher penalty for high DTI ratios:
```diff
-    if debt_income_ratio > 80:
-        score -= 30
+    if debt_income_ratio > 80:
+        score -= 45  # Increased penalty
```

---

## 4. Coding Standards

* **Python Guidelines (PEP 8)**: Use 4 spaces for indentation. Use descriptive function and variable names in snake_case. Include docstrings for complex logic.
* **JavaScript Guidelines**: Write React components as functional components using hooks. Keep components modular and avoid inline styles where possible, utilizing global design tokens.
* **Pydantic Schemas**: Keep request payloads separated from database ORM schemas, utilizing Pydantic schemas in the `schemas/` folder.
