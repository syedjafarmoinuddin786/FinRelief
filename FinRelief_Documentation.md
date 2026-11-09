# FinRelief — Project Documentation

**Repo:** https://github.com/syedjafarmoinuddin786/FinRelief
**Tagline:** AI-Powered Debt Relief & Financial Recovery Platform

> **Sync note:** This documentation describes the *fixed* codebase delivered as `FinRelief-fixed.zip` earlier in this conversation. The GitHub repo linked above still has the pre-fix code as of this writing — push the fixed files up (see Section 11) for the repo to match what's described here.

---

## 1. Overview

FinRelief helps a user enter their financial snapshot (debt, income, expenses) and get back an AI-generated, actionable debt-relief plan. It has user accounts (signup/login with JWT), a FastAPI backend, a SQLite database via SQLAlchemy, and a Gemini-powered advice engine. The frontend is a single-page vanilla HTML/CSS/JS app with a glassmorphism UI.

## 2. Architecture

| Layer | Tech |
|---|---|
| Backend | FastAPI (Python) |
| Frontend | Vanilla HTML/CSS/JS |
| Database | SQLite via SQLAlchemy ORM (tables auto-created on startup) |
| Auth | OAuth2 password flow + JWT (`python-jose`) |
| Password hashing | `bcrypt`, called directly (no `passlib`) |
| AI | Google Gemini (`google-genai` SDK, model configurable via `GEMINI_MODEL`, default `gemini-3.5-flash`) |
| Testing | `pytest` (`backend/tests/test_api.py`) |
| Package/env manager | `uv` |

### Request flow (debt analysis)
```
Frontend form → POST /api/analyze-debt (Bearer token)
   → routes.py validates the token via get_current_user()
   → services/ai_service.py builds a prompt and calls Gemini
   → routes.py logs the advice to AIHistory via crud.log_ai_history()
   → Markdown advice returned to frontend
   → frontend renders it with marked.js
```

## 3. Project Structure

```
FinRelief/
├── backend/
│   ├── requirements.txt
│   ├── .env.example          # documents every supported env var
│   ├── test_db.py            # manual script: exercises CRUD (user, profile, loan)
│   ├── test_epic2.py         # manual script: signs up a user, then calls /api/analyze-debt with its token
│   ├── tests/
│   │   └── test_api.py       # pytest suite (9 tests), Gemini call stubbed
│   └── app/
│       ├── main.py           # FastAPI app, table creation on startup, CORS, root/health routes
│       ├── api/
│       │   └── routes.py     # signup, login, analyze-debt, ai-history, loans endpoints
│       ├── core/
│       │   └── security.py   # JWT creation/verification, secret key from env
│       ├── db/
│       │   ├── database.py   # SQLAlchemy engine/session (SQLite)
│       │   ├── models.py     # User, FinancialProfile, Loan, AIHistory, SettlementPrediction, AINegotiation
│       │   └── crud.py       # user/profile/loan/ai-history CRUD + bcrypt password hashing
│       └── services/
│           └── ai_service.py # Gemini call + error handling
└── frontend/
    ├── index.html
    ├── styles.css
    └── app.js                # API_BASE_URL centralized at the top of the file
```

## 4. Data Model

Defined in `backend/app/db/models.py`, all backed by SQLite (`finrelief.db`):

- **User** — `UserID, Name, Email, Password (hashed), MonthlyIncome, MonthlyExpenses`
- **FinancialProfile** (1:1 with User) — `EMI_Ratio, DTI_Ratio, MonthlySurplus, StressLevel`
- **Loan** (1:many with User) — `LenderName, LoanType, OutstandingAmount, InterestRate, EMI, OverdueMonths`
- **SettlementPrediction** (per Loan) — `SuggestedSettlement, RiskCategory, PredictedAmount`
- **AIHistory** (per User) — `GeneratedContent, QueryType, Timestamp`
- **AINegotiation** (per User+Loan) — `NegotiationStrategy, NegotiationLetter, GeneratedDate`

**Wiring status per table:**
| Table | CRUD functions | Route(s) |
|---|---|---|
| User | Yes | `/api/signup`, `/api/login` |
| Loan | Yes | `/api/loans` (POST + GET) |
| AIHistory | Yes | Auto-logged by `/api/analyze-debt`; read via `/api/ai-history` |
| FinancialProfile | Yes (`create_or_update_financial_profile`) | **None** — no route calls it, so a user's EMI/DTI ratio and stress level can't actually be set through the API yet |
| SettlementPrediction | **None** | **None** — schema-only |
| AINegotiation | **None** | **None** — schema-only |

## 5. API Reference

Base prefix: `/api`

| Method | Path | Auth | Body | Returns |
|---|---|---|---|---|
| GET | `/` | none | — | `{"message": "Welcome to FinRelief API"}` |
| GET | `/health` | none | — | `{"status": "healthy"}` |
| POST | `/api/signup` | none | `{name, email, password, income, expenses}` | `{access_token, token_type}` |
| POST | `/api/login` | none | OAuth2 form (`username`=email, `password`) | `{access_token, token_type}` |
| POST | `/api/analyze-debt` | Bearer JWT | `{total_debt, monthly_income, monthly_expenses}` | `{advice: "<markdown>"}` — also logs an `AIHistory` row |
| GET | `/api/ai-history` | Bearer JWT | — | list of `{HistoryID, GeneratedContent, QueryType}`, newest first |
| POST | `/api/loans` | Bearer JWT | `{lender_name, loan_type, outstanding_amount, interest_rate, emi, overdue_months}` (`overdue_months` defaults to 0) | the created Loan record |
| GET | `/api/loans` | Bearer JWT | — | list of the current user's Loan records |

Auth details:
- Token is a JWT signed HS256. Expiry is configurable via `ACCESS_TOKEN_EXPIRE_MINUTES` (default 60 minutes). Payload `sub` = user email.
- Every Bearer-protected route depends on `get_current_user`, which decodes the token and looks up the user by email.
- Logout is client-side only (clears `localStorage`) — a token remains valid server-side until it expires.

## 6. AI Service

`services/ai_service.py::analyze_financials()`:
- Builds a prompt asking Gemini to compute disposable income and return a 3-step debt plan in Markdown.
- Calls the model named in `GEMINI_MODEL` (defaults to `gemini-3.5-flash`) via the `google-genai` client, which reads `GEMINI_API_KEY` from the environment automatically.
- Maps Gemini `APIError` codes 503/429 to friendly messages; anything else raises a generic error, which `routes.py` turns into an HTTP 500 with the message as `detail`.

## 7. Frontend

Single page (`index.html`) with three interactive parts, all wired in `app.js`:
1. **Health check** — pings `GET /health` at `API_BASE_URL` on load and shows connection status.
2. **Auth modal** — toggles between Login/Sign Up, stores the JWT in `localStorage` under `finrelief_token`.
3. **Financial form** — requires a token (opens the auth modal if missing), posts to `/api/analyze-debt` with a 30-second abort timeout, renders the returned Markdown advice with `marked.js`.

The backend URL is a single constant at the top of `app.js`:
```js
const API_BASE_URL = window.FINRELIEF_API_BASE_URL || "http://localhost:8000";
```
All four fetch calls (health check, login, signup, analyze-debt) use this constant. It still defaults to `localhost:8000`, so it only works against a locally running backend out of the box — but deploying now just means setting `window.FINRELIEF_API_BASE_URL` before `app.js` loads, instead of editing four separate fetch calls.

## 8. Setup & Running Locally

**Backend:**
```bash
cd backend
uv run uvicorn app.main:app --reload
```

Copy `backend/.env.example` to `backend/.env` and fill it in:

| Variable | Required? | Default if unset |
|---|---|---|
| `GEMINI_API_KEY` | Yes | none — Gemini calls fail without it |
| `GEMINI_MODEL` | No | `gemini-3.5-flash` |
| `JWT_SECRET_KEY` | Required for production | falls back to a publicly-known dev string (with a console warning) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `60` |
| `CORS_ALLOWED_ORIGINS` | No | local-dev origins only (`localhost`/`127.0.0.1` on ports 8000 and 5500) |

Database tables are created automatically on startup — no manual step needed.

**Frontend:**
Serve `frontend/index.html` with any static/live server (e.g. VS Code Live Server) so it can reach the backend at `http://localhost:8000` (or wherever you've pointed `API_BASE_URL`).

**Running tests:**
```bash
cd backend
pytest -v
```
9 tests, Gemini call stubbed so no API key is required to run them.

**Manual test scripts** (kept for reference; `pytest` is now the primary way to verify the app):
```bash
python backend/test_db.py       # exercises user/profile/loan CRUD directly
python backend/test_epic2.py    # signs up a throwaway user, then calls /api/analyze-debt with its token — needs a real GEMINI_API_KEY to fully succeed
```

## 9. Current Limitations / Things to Flag Before Production

- **FinancialProfile is never written** — the CRUD function exists but no route calls it, so EMI ratio, DTI ratio, and stress level can't be set via the API today.
- **SettlementPrediction and AINegotiation are schema-only** — no CRUD functions and no routes; nothing reads or writes these tables.
- **`JWT_SECRET_KEY` fallback is silent** — if you forget to set it, the app starts anyway using the same publicly-known dev string, with only a console warning (not a hard failure).
- **No token refresh or server-side revocation** — a token stays valid for its full lifetime even after a client-side "logout."
- **No rate limiting** on `/api/signup` or `/api/login` — vulnerable to brute-force/credential-stuffing if exposed publicly.
- **Minimal input validation** — Pydantic enforces types, but nothing stops `monthly_expenses` exceeding `monthly_income`, negative debt, etc.
- **`CORS_ALLOWED_ORIGINS` defaults to local-dev origins only** — must be set explicitly to your real frontend's origin before deploying.

## 10. Roadmap (per README, with current status)

- **Epic 1 (done):** scaffolding, FastAPI setup, frontend styling/base logic, `uv` env.
- **Epic 2 (further along than the README suggests):** auth (signup/login) is complete; AI debt analysis, AI-history logging, and loan tracking are all wired end-to-end.
- **Epic 3 (upcoming per README, partially done):** SQLite persistence is fully wired for User, Loan, and AIHistory. FinancialProfile, SettlementPrediction, and AINegotiation still need routes/CRUD.

## 11. Recent Fixes Applied (2026-07-20)

**Bugs fixed:**
- The app never created its own DB tables outside the manual `test_db.py` script — a fresh clone would 500 on the very first signup with `no such table: users`. `main.py` now calls `Base.metadata.create_all()` on startup.
- `passlib` (last released 2020, effectively unmaintained) is incompatible with modern `bcrypt` (≥4.1), which broke every signup/login on a fresh `pip install`. Password hashing now calls `bcrypt` directly; `passlib` was removed from `requirements.txt`.
- `test_epic2.py` called `/api/analyze-debt` with no Bearer token and would 401 against the (already-protected) route. It now signs up a throwaway user first and uses its token.

**New functionality:**
- `AIHistory` is now written on every successful `/api/analyze-debt` call, plus a new `GET /api/ai-history`.
- `Loan` CRUD existed but had no routes — added `POST /api/loans` and `GET /api/loans`.
- Added `backend/tests/test_api.py`, a real `pytest` suite (9 tests, Gemini stubbed) — previously the only tests were print-only manual scripts with no assertions.

**Hardening:**
- `SECRET_KEY` now reads from `JWT_SECRET_KEY` (dev fallback + warning instead of a hardcoded prod secret).
- CORS no longer wildcards origins while allowing credentials (invalid per the CORS spec); origins are now configurable via `CORS_ALLOWED_ORIGINS`.
- Gemini model name is configurable via `GEMINI_MODEL`.
- Frontend's 4 hardcoded `localhost:8000` calls consolidated into one `API_BASE_URL` constant.
- Added `backend/.env.example`.
- Fixed Pydantic v2 `class Config` and `datetime.utcnow()` deprecation warnings.

**Not yet pushed:** these fixes exist in the local project and in `FinRelief-fixed.zip` shared in this conversation, but not yet in the GitHub repo — see the sync note at the top of this document.
