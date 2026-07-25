# APPENDIX

This appendix provides a summary of configuration files, environment variables, folder mappings, abbreviations, and a glossary for the **FinRelief AI** platform.

---

## A.1 Detailed Folder Structure Explanations

Here is a map of the file locations in the repository:

* **[Cover Page](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/Documentation/01_Cover_Page.md)**
* **[Certificate](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/Documentation/02_Certificate.md)**
* **[Acknowledgement](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/Documentation/03_Acknowledgement.md)**
* **[Abstract](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/Documentation/04_Abstract.md)**
* **[Table of Contents](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/Documentation/05_Table_of_Contents.md)**
* **[Chapter 1 — Introduction](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/Documentation/06_Chapter1_Introduction.md)**
* **[Chapter 2 — Literature Survey](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/Documentation/07_Chapter2_Literature_Survey.md)**
* **[Chapter 3 — Requirement Analysis](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/Documentation/08_Chapter3_Requirement_Analysis.md)**
* **[Chapter 4 — System Analysis](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/Documentation/09_Chapter4_System_Analysis.md)**
* **[Chapter 5 — System Design](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/Documentation/10_Chapter5_System_Design.md)**
* **[Chapter 6 — Implementation](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/Documentation/11_Chapter6_Implementation.md)**
* **[Chapter 7 — Testing](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/Documentation/12_Chapter7_Testing.md)**
* **[Chapter 8 — Results](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/Documentation/13_Chapter8_Results.md)**
* **[Chapter 9 — Future Enhancements](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/Documentation/14_Chapter9_Future_Enhancements.md)**
* **[Chapter 10 — Conclusion](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/Documentation/15_Chapter10_Conclusion.md)**
* **[References](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/Documentation/16_References.md)**
* **[Appendix](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/Documentation/17_Appendix.md)**

---

## A.2 Configuration & Environment Variables

The backend application requires configuration via a `.env` file located in the `backend/` root directory. Below is the standard template of the environment variables without any sensitive credentials:

```env
# Server Mode configuration
DEBUG=True
ENVIRONMENT=development

# Database location URL (SQLite default)
DATABASE_URL=sqlite:///./finrelief.db

# JWT Signature credentials (replace with secure key)
SECRET_KEY=change-me-generate-with-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120

# Google Gemini API key (Required for advanced AI capabilities)
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## A.3 Deployment Guide

To deploy **FinRelief AI** to a production Linux server (e.g., Ubuntu VPS), follow these instructions:

### 1. Backend Service Configuration (using systemd & Gunicorn)
Create a systemd service file `/etc/systemd/system/finrelief-backend.service`:
```ini
[Unit]
Description=FinRelief AI FastAPI Backend
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/FinRelief-AI/backend
ExecStart=/var/www/FinRelief-AI/backend/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000
Restart=always

[Install]
WantedBy=multi-user.target
```
Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable finrelief-backend
sudo systemctl start finrelief-backend
```

### 2. Frontend Production Build (using Nginx)
Compile the static build:
```bash
cd frontend
npm install
npm run build
```
Copy files to `/var/www/html/finrelief/` and configure the Nginx server block to serve static assets and proxy `/api` calls:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        root /var/www/html/finrelief/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api/v1 {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## A.4 Glossary & Abbreviations

### Glossary
* **Debt Settlement**: An agreement between a lender and borrower to resolve an outstanding debt for a reduced lump-sum payment, considered as settled.
* **Hardship Letter**: A formal written correspondence explaining to a creditor the financial reasons (e.g., job loss, medical emergency) why the borrower cannot fulfill regular loan obligations.
* **Glassmorphism**: A modern UI design trend featuring semi-transparent backgrounds with a blurred effect, mimicking frosted glass.
* **Fallback Engine**: A rule-based backup algorithm that executes locally when external APIs are offline or unavailable.
* **SQLAlchemy ORM**: A Python library that maps database tables to classes, allowing developers to write database queries using Python code instead of raw SQL.

### Abbreviations
* **API**: Application Programming Interface
* **JWT**: JSON Web Token
* **DTI**: Debt-to-Income Ratio
* **EMI**: Equated Monthly Installment
* **CRUD**: Create, Read, Update, Delete
* **OTS**: One-Time Settlement
* **LLM**: Large Language Model
* **SPA**: Single Page Application
* **CORS**: Cross-Origin Resource Sharing
* **WAL**: Write-Ahead Logging
* **CIBIL**: Credit Information Bureau (India) Limited
