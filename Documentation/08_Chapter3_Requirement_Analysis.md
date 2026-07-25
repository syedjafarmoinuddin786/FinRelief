# Chapter 3 — Requirement Analysis

This chapter details the functional, non-functional, hardware, software, and technology requirements of the **FinRelief AI** platform.

---

## 3.1 Functional Requirements

1. **User Authentication & Session Management**:
   * The system must allow users to register an account with their email, password, and full name.
   * The system must support JWT-based login, generating a secure access token stored on the client.
   * The system must protect private routes so only authenticated users can view dashboards, manage loans, and access AI features.

2. **Loan Portfolio Management (CRUD)**:
   * Users must be able to create, read, update, and delete individual loans.
   * For each loan, the system must record the loan type (Personal, Home, Auto, Credit Card, Student, Business), lender name, original amount, outstanding balance, interest rate, EMI amount, tenure months, overdue months, and loan status.
   * Any change in the loan list must automatically trigger database updates and update the financial profile.

3. **Financial Health Calculation Engine**:
   * The system must calculate the total EMI, total outstanding debt, monthly surplus, EMI-to-income ratio, and Debt-to-Annual-Income ratio.
   * The system must compute a Financial Health Score (1–100) and assign a stress level (Low, Medium, High, Critical) using a penalized scoring rule.
   * The financial profile must be persisted to the database and updated in real-time.

4. **Settlement Target Predictor**:
   * The system must predict recommended lump-sum settlement targets (amount and percentage) based on the loan type, interest rate, and overdue months.
   * It must assign a priority level (Low, Medium, High, Critical) and lender risk category (Low, Moderate, High, Critical).

5. **Dual AI Letter & Strategy Generator**:
   * The system must draft formal hardship negotiation letters and custom negotiation strategies.
   * If the Google Gemini API key is configured, the system must leverage the `gemini-pro` model to generate highly personalized letters.
   * If the API key is missing or offline, the system must trigger a local fallback engine to output rules-based templates.

6. **Interactive counselor Chat**:
   * Users must be able to chat with an AI counselor regarding budgeting, saving, credit scoring, and debt resolution.
   * The chat must be context-aware, incorporating the user's income, expenses, and outstanding debts into the chat prompts.

7. **Audit & Logs History**:
   * The system must record and list all predicted settlement offers and generated AI strategies, letters, and chat interactions.
   * History tables must support pagination and be queryable via API.

---

## 3.2 Non-Functional Requirements

1. **Security**:
   * High-grade encryption: User passwords must be hashed using `bcrypt` before database storage.
   * API Security: All routers (except `/auth/register` and `/auth/login/json`) must require a valid JWT token in the `Authorization: Bearer <token>` header.
2. **Performance**:
   * API endpoints must process requests under 500 milliseconds (excluding external Gemini API round-trip times).
   * SQLite deletion journal must operate with `PRAGMA journal_mode=DELETE` and `PRAGMA synchronous=NORMAL` to prevent locking issues.
3. **Resiliency & Reliability**:
   * Graceful degradation: The application must not crash if the Gemini API key is invalid. It must seamlessly transition to fallback templates and notify the client using the `is_fallback` flag.
4. **Usability**:
   * The interface must utilize a clean, premium, dark glassmorphic layout.
   * Elements must be responsive across desktop and mobile devices.
5. **Modularity**:
   * Clear separation of concerns between database models, Pydantic validation schemas, business logic services, and API controllers.

---

## 3.3 Hardware Requirements

### Developer Machine / Server
* **Processor**: Dual-Core 2.0 GHz or higher (x64 architecture).
* **RAM**: 8 GB minimum (16 GB recommended for running dev servers).
* **Storage**: 500 MB of free disk space (to house virtual environments, node modules, and local SQLite database files).

### Client Device (End User)
* **Device**: Laptop, desktop, or mobile phone.
* **Network**: Active internet connection (to connect to backend APIs and the Gemini model).

---

## 3.4 Software Requirements

* **Operating System**: Windows 10/11, macOS, or Linux (Ubuntu 20.04+).
* **Python Runtime**: Version 3.11.0 or higher.
* **Node.js Runtime**: Version 18.0.0 or higher, with `npm` package manager.
* **Web Browser**: Modern browser (Chrome 100+, Edge 100+, Safari 15+, Firefox 100+).

---

## 3.5 Technology Stack

* **Frontend**: React.js (v18), Vite build tool, Vanilla CSS variables, Axios HTTP client, Lucide Icons, React Router DOM (v6).
* **Backend**: FastAPI (Python), Uvicorn server, Pydantic (v2) request/response validation, SQLAlchemy ORM.
* **Database**: SQLite (SQLAlchemy engine), relational sqlite3 binary driver.
* **Security & Auth**: PyJWT / python-jose for token generation, Passlib with bcrypt for hashing.
* **AI API Integration**: Google Generative AI Python SDK (`google-generativeai==0.5.4`).

---

## 3.6 System Constraints & Assumptions

### Constraints
1. **Local Database**: SQLite is a file-based database, which is single-user write-locked. Concurrent writes are handled via queueing in the SQLAlchemy session factory.
2. **Vite Proxy**: Local development relies on Vite's local dev server proxy configured in `vite.config.js` to route `/api/v1` calls to `http://localhost:8000`.
3. **API Limits**: Advanced AI counseling relies on free/paid tiers of Google Gemini. If API limits are exceeded, the app defaults to fallback rules.

### Assumptions
1. The user will input truthful financial data. Outgoing expenses and loan balances must be numeric values.
2. The browser supports modern CSS properties (backdrop-filter, variables) to render the glassmorphic theme.
