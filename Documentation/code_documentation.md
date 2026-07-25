# Code & Components Documentation

This document describes the modules, services, and UI components of the **FinRelief AI** platform, explaining their responsibilities and integrations.

---

## 1. Backend Core & Services

### 1.1 Configuration & Database Connectors
* **[config.py](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/backend/app/config.py)**: Loads configuration parameters from the environment and `.env` file using Pydantic Settings. It validates that JWT encryption keys, token lifespan limits, CORS origins, and external API keys are configured correctly.
* **[database.py](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/backend/app/database.py)**: Sets up the SQLAlchemy engine. It converts relative SQLite URLs into absolute paths and sets database pragmas (`PRAGMA journal_mode=DELETE` and `PRAGMA synchronous=NORMAL`) to resolve locking errors.
* **[dependencies.py](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/backend/app/auth/dependencies.py)**: Implements dependency injection for user validation. It decodes the JWT from incoming request headers, verifies the signature, and retrieves the active `User` record from the database.

### 1.2 Mathematical & AI Service Engines
* **[financial_engine.py](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/backend/app/services/financial_engine.py)**: Calculates financial ratios. It calculates monthly surplus cash, EMI ratios, and DTI metrics, applying penalty rules to compute a final Financial Health Score and Stress Level.
* **[settlement_engine.py](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/backend/app/services/settlement_engine.py)**: Recommends settlement payout targets. It evaluates loan types, interest rates, and overdue periods to predict recommended settlement amounts and risk categories.
* **[gemini_service.py](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/backend/app/services/gemini_service.py)**: Connects to the Google Gemini API. It builds structured prompts containing the user's financial details and handles API requests.
* **[fallback_engine.py](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/backend/app/services/fallback_engine.py)**: Implements the rule-based fallback engine. It generates standard negotiation strategies and hardship letters when the Gemini API is offline or unconfigured.
* **[ai_orchestrator.py](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/backend/app/services/ai_orchestrator.py)**: Manages AI requests. It attempts to call the Gemini API, handles exceptions, triggers the fallback engine if needed, and saves transactions to the `ai_history` table.

---

## 2. Frontend State & Interceptors

### 2.1 Global Context
* **[AuthContext.jsx](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/frontend/src/context/AuthContext.jsx)**: Manages global authentication state. It checks for stored JWT tokens on startup, retrieves user profiles, and provides `login`, `register`, and `logout` functions across the application.

### 2.2 API Connection Client
* **[api.js](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/frontend/src/services/api.js)**: Configures the Axios HTTP client. It automatically injects the JWT token into request headers and intercepts `401 Unauthorized` responses to handle logouts gracefully.

---

## 3. UI Views & Pages

* **[Dashboard.jsx](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/frontend/src/pages/Dashboard.jsx)**: The central hub of the application. It displays financial health metrics (surplus, DTI, health score) and hosts the interactive AI Counselor chat window.
* **[LoanManagement.jsx](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/frontend/src/pages/LoanManagement.jsx)**: Shows the user's loan portfolio, outstanding amounts, and payment statuses, with buttons to add, edit, or delete records.
* **[SettlementPredictor.jsx](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/frontend/src/pages/SettlementPredictor.jsx)**: Selects a loan, calls the settlement prediction endpoint, and displays recommended target lump-sums, priorities, and negotiation strategies.
* **[NegotiationEmailGenerator.jsx](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/frontend/src/pages/NegotiationEmailGenerator.jsx)**: A form to generate formal hardship letters. Users select a loan, enter their hardship reason, and generate the negotiation letter.
* **[AIHistory.jsx](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/frontend/src/pages/AIHistory.jsx)**: A paginated log of past AI-generated strategies, letters, and counselor chat records.
* **[KnowYourRights.jsx](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/frontend/src/pages/KnowYourRights.jsx)**: Displays financial education content regarding debtor rights, collection limits, and standard debt collection practices.
