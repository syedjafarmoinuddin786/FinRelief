# Chapter 4 — System Analysis

System analysis involves a comprehensive study of the proposed system to determine its viability, feasibility, operational constraints, and associated risk vectors.

---

## 4.1 Feasibility Study
A feasibility study evaluates whether the development of **FinRelief AI** is justified under economic, technical, and operational dimensions.

---

## 4.2 Economic Feasibility
The project is economically highly feasible, both for development and deployment:
* **Zero Software Licensing Costs**: The entire tech stack (FastAPI, React, SQLite, Python, Node.js) consists of open-source software with permissive licenses (MIT/BSD/Apache), resulting in no license fees.
* **Low Hosting Footprint**: The application uses SQLite as an embedded database, removing the cost of dedicated SQL server clusters (such as PostgreSQL or MySQL instances). The entire application can be hosted on a basic, low-cost virtual private server (VPS) or cloud instance (e.g., Render, AWS EC2 Micro, or Heroku).
* **AI Cost Controls**: The Google Gemini API provides a generous free tier for developers. The rule-based local fallback engine acts as a shield, ensuring that even if the developer exhausts the free tier or decides not to configure an API key, the core systems function without cost.
* **Savings for the End User**: The application is free for users, saving them from the high fees (15% to 25% of outstanding balances) charged by third-party debt settlement agencies.

---

## 4.3 Technical Feasibility
The platform is technically viable based on modern web development practices:
* **Proven Stack**: React is the industry standard for fast, responsive single-page applications. FastAPI is one of the fastest Python frameworks available, utilizing asynchronous ASGI server capabilities (Uvicorn) and automatic OpenAPI documentation generation.
* **Database Resiliency**: SQLAlchemy handles connection pooling and session lifecycle management. By using specific database pragmas (`journal_mode=DELETE` and `synchronous=NORMAL`), SQLite is optimized to avoid locking errors even when run in synced desktop folders like OneDrive.
* **Algorithmic Fallback**: The development team has engineered a rule-based backup engine inside `fallback_engine.py`. This ensures that technical failures in the Google Gemini API (such as timeouts, rate-limits, or bad API keys) do not crash the application.
* **Lightweight Footprint**: The total build output of the frontend is minimal (less than 2 MB), and the backend dependencies are standard, easily installable packages.

---

## 4.4 Operational Feasibility
Operationally, the platform fits the needs of its target user base:
* **User-Friendly Interface**: The frontend features a clear, dark-themed, glassmorphic layout. It does not require specialized financial training. Budgets and loans are presented in simple forms, and the dashboard aggregates these into clear visual metrics (ratios, scores, levels).
* **Empowerment Model**: Instead of acting as an intermediary, the system gives users the tools (hardship letters, negotiation timelines) to represent themselves, making it operationally simple and legally safe.
* **Self-Contained Deployment**: Developers or users can launch the application locally using simple batch scripts (`run_backend.bat` and `run_frontend.bat`), which handles the execution environment automatically.

---

## 4.5 Risk Analysis

The development and deployment of FinRelief AI face several risks, which have been mitigated through design decisions:

### 1. API Key Exposure Risk
* **Risk**: Users or developers might accidentally hardcode their Google Gemini API keys in the source code or commit them to public GitHub repositories.
* **Mitigation**: The system uses `pydantic-settings` to load settings from an external `.env` file, which is ignored in `.gitignore`. The client key is never exposed to the frontend; the React SPA communicates only with the FastAPI backend, which handles API interactions securely.

### 2. SQLite Database Locking
* **Risk**: SQLite can experience database locking errors if the database file (`finrelief.db`) is active in a folder synced by cloud storage services (like OneDrive, Google Drive, or Dropbox) due to write locks.
* **Mitigation**: Database engines are configured with `connect_args = {"check_same_thread": False, "timeout": 30}` to retry locks, and the database connection listeners execute `PRAGMA journal_mode=DELETE` and `PRAGMA synchronous=NORMAL` to keep transactions brief and localized.

### 3. User Credit Score Impact
* **Risk**: Users might mistakenly believe that debt settlement has zero negative consequences.
* **Mitigation**: The generated strategies and counselor replies clearly state that settled accounts stay on credit reports for 7 years and can negatively affect credit ratings, encouraging users to make informed decisions.
