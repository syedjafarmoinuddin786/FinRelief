# Full Stack Development Project Documentation
*Adapted from FSD Documentation Format Template*

## 1. Introduction
- **Project Title:** FinRelief
- **Project Type:** Full Stack Application (Decoupled Architecture)

## 2. Project Overview
- **Purpose:** To provide personalized, AI-driven financial advice for debt relief and wealth generation. FinRelief analyzes users' income, expenses, and debt to generate actionable, empathetic financial roadmaps.
- **Features:**
  - Secure User Authentication (JWT + Password Hashing)
  - Interactive "Glassmorphism" User Interface
  - AI-Powered Debt Analysis using Google Gemini 2.5 Flash
  - Secure Data Storage using SQLite and SQLAlchemy ORM

## 3. Architecture
- **Frontend:** Vanilla HTML5, CSS3, and JavaScript. Uses the Fetch API to securely communicate with the backend. Styled using modern CSS variables, animations, and a responsive glassmorphism design system.
- **Backend:** Python FastAPI. Implements a highly scalable REST API, CORS middleware, JWT token verification, and integration with the Google GenAI SDK.
- **Database:** SQLite managed via SQLAlchemy ORM. The schema includes a `users` table for secure credential storage.

## 4. Setup Instructions
- **Prerequisites:** 
  - Python 3.10+
  - Google Gemini API Key
  - Node.js (Optional, if using an alternative local server like `http-server`)
- **Installation:**
  1. Clone the repository: `git clone <repository_url>`
  2. Create a virtual environment in the `backend/` directory: `python -m venv .venv`
  3. Activate the virtual environment and install dependencies: `pip install -r backend/requirements.txt`
  4. Set environment variables (e.g., `GEMINI_API_KEY`, `SECRET_KEY`) in a `.env` file in the backend directory.

## 5. Folder Structure
- **Frontend (`/frontend`):**
  - `index.html`: The main user interface and layout.
  - `styles.css`: Styling rules, animations, and color palettes.
  - `app.js`: Client-side logic, DOM manipulation, and API fetching.
- **Backend (`/backend/app`):**
  - `main.py`: FastAPI entry point and CORS configuration.
  - `api/routes.py`: API endpoint definitions (signup, login, analyze-debt).
  - `core/security.py`: JWT generation and password hashing.
  - `models/database.py`: SQLAlchemy models and engine configuration.
  - `services/ai_service.py`: Google Gemini API integration and error handling.

## 6. Running the Application
A convenience script `start_finrelief.bat` is provided at the root of the project to start both servers simultaneously. Alternatively, you can run them manually:
- **Backend:** Navigate to `/backend` and run `uvicorn app.main:app --reload --port 8000`
- **Frontend:** Navigate to `/frontend` and run `python -m http.server 3000`

## 7. API Documentation
- `POST /api/signup`: Creates a new user account. Expects JSON with `username` and `password`. Returns a JWT access token.
- `POST /api/login`: Authenticates an existing user. Expects JSON with `username` and `password`. Returns a JWT access token.
- `POST /api/analyze-debt`: Submits financial data for AI analysis. Expects JSON with `total_debt`, `monthly_income`, and `monthly_expenses`. Requires a valid `Authorization: Bearer <token>` header. Returns markdown-formatted AI advice.

## 8. Authentication
Authentication is managed via JSON Web Tokens (JWT). When a user logs in or signs up, the backend issues an access token. The frontend stores this token in `localStorage` and attaches it to the `Authorization` header for all protected API requests. Passwords are securely hashed in the database using `passlib` (bcrypt).

## 9. User Interface
The UI is built with a bespoke "glassmorphism" aesthetic featuring:
- Frosted glass containers over animated, dynamic gradient backgrounds.
- High-contrast, elegant typography.
- Loading spinners during asynchronous operations.
- Real-time error handling with user-friendly alerts.

## 10. Testing
- **Backend:** Tested using tools like `curl` and browser network inspection to ensure endpoints return expected HTTP status codes (200 OK, 401 Unauthorized, 503 Service Unavailable).
- **Frontend:** Functional manual testing to ensure smooth navigation, correct token injection, and responsive design across device sizes.

## 11. Known Issues
- The AI service requires a valid internet connection; high latency from the Gemini API can occasionally trigger the frontend's 30-second `AbortController` timeout.

## 12. Future Enhancements
- Integration with external banking APIs for automatic transaction syncing.
- Migrating the database from SQLite to PostgreSQL for production deployment.
- Abstracting hardcoded `localhost` URLs to support environment-based configuration for cloud deployment.
