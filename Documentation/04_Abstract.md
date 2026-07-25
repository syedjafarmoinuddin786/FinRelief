# ABSTRACT

In contemporary personal finance, outstanding debt accumulation represents a major socioeconomic challenge for individuals. Borrowers experiencing financial distress often face severe psychological stress, aggressive debt collection tactics, and limited clarity on potential paths to resolution. Although debt settlement offers a viable alternative to bankruptcy, traditional solutions require hiring third-party settlement agencies, which charge high fees and introduce substantial financial risks.

This project introduces **FinRelief AI**, an autonomous, secure, and user-centric software platform designed to democratize access to financial recovery and debt negotiation tools. The platform empowers users to manage their loan portfolios, calculate their debt-to-income (DTI) metrics, compute an objective financial health score, and prioritize creditor settlement negotiation actions.

### Core Architecture and Features
1. **Financial Health & Risk Analysis**: Computes real-time cash flow surplus, EMI ratios, DTI ratios, and assigns stress levels (Low, Medium, High, Critical) using a mathematical scoring engine.
2. **Rule-Based Settlement Predictor**: Classifies lender risk, establishes recommended lump-sum settlement percentages (ranging from 30% to 90%), and defines strategic negotiation timelines.
3. **AI-Powered Negotiation & Counselor Chat**: Integrates the **Google Gemini API** (via the `google-generativeai` SDK) to draft formal hardship and negotiation letters and drive a contextual AI financial counselor chat interface.
4. **Resilient Local Fallback Engine**: Employs a robust, rule-based algorithmic financial fallback service that activates automatically if the external AI API is unconfigured or offline, ensuring uninterrupted platform utility.

### Technology Stack
* **Frontend**: React.js (v18), React Router (v6), Vite, Vanilla CSS, Axios, Lucide Icons.
* **Backend**: Python (v3.11+), FastAPI, Uvicorn, SQLAlchemy ORM, Pydantic (v2).
* **Database**: SQLite (local development database with WAL-safe deletion journaling).
* **Security**: JWT-based session authorization, bcrypt password hashing.

### Results
The resulting application provides an interactive, dark-themed, glassmorphic dashboard showcasing real-time metrics, dynamic charts, loan management tables, settlement predictions, and an interactive counselor window. It successfully resolves dependency hurdles and functions as a secure, high-performance web tool for personal financial recovery.
