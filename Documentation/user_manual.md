# User Manual & Getting Started Guide

This user-friendly manual explains how to install, configure, run, and use the **FinRelief AI** platform.

---

## 1. Installation and Local Setup

### Prerequisites
Ensure your system has the following software installed:
* **Python** (version 3.11 or higher)
* **Node.js** (version 18 or higher) and npm

---

### Step 1: Clone the Repository
Open a terminal (or PowerShell on Windows) and run:
```bash
git clone https://github.com/SumaSri8406/FinRelief-AI.git
cd FinRelief-AI
```

---

### Step 2: Configure Environment Variables
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Copy the environment template to create your `.env` file:
   * **Windows (Command Prompt)**: `copy .env.example .env`
   * **Linux/macOS/PowerShell**: `cp .env.example .env`
3. Open the `.env` file in a text editor.
4. (Optional) Set your Google Gemini API Key:
   ```env
   GEMINI_API_KEY=AIzaSyC...your_real_key_here
   ```
   *If you do not configure an API key, the platform will automatically use the local rule-based fallback engine.*

---

### Step 3: Run the Application (Windows Automated Scripts)
If you are on Windows, you can start the application using the included batch scripts:
1. Double-click `run_backend.bat` in the root folder to start the FastAPI server.
2. Double-click `run_frontend.bat` in the root folder to start the React client.

---

### Step 4: Run the Application Manually

#### 1. Start the Backend:
```bash
cd backend
python -m venv venv
# Activate the environment:
# Windows (PowerShell): .\venv\Scripts\activate
# Linux/macOS: source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```
The backend API server will start at `http://127.0.0.1:8000`.

#### 2. Start the Frontend:
```bash
cd ../frontend
npm install
npm run dev
```
The frontend application will start at `http://localhost:3000`. Open this address in your web browser.

---

## 2. Feature Guide

### 2.1 Registration & Login
1. Open `http://localhost:3000` in your web browser.
2. Click **Register** and fill out the form (Full Name, Email, and Password).
3. Once registered, log in to access your dashboard.

### 2.2 Configure Monthly Budget
1. Click **Manage Budget** on the dashboard (or go to **Profile** in the sidebar).
2. Enter your **Monthly Income** and **Monthly Essential Expenses**.
3. Click **Save Budget**. The financial engine will compile your health metrics.

### 2.3 Populate Loan Portfolio
1. Go to the **Loans** section in the sidebar.
2. Click **Add Loan Record**.
3. Enter the loan details:
   * **Lender Name** (e.g., SBI, HDFC)
   * **Loan Type** (Credit Card, Personal, Home, Auto, Student, Business)
   * **Original Amount** & **Outstanding Amount**
   * **Interest Rate** (Annual Percentage Rate)
   * **Monthly EMI** & **Overdue Months**
4. Click **Create Loan**. You can edit or delete these loans at any time.

### 2.4 Analyze Dashboard Metrics
* **Total Outstanding Debt**: The sum of all active and defaulted loan balances.
* **Monthly Surplus**: Your remaining cash after expenses and EMI payments.
* **Debt to Income (DTI)**: Your debt-to-annual-income ratio.
* **Financial Health Score**: An overall health rating from 0 to 100.
* **AI Chat Counselor**: Type questions in the chat window on the dashboard for instant advice.

### 2.5 Predict Settlement Targets
1. Go to **Settlement Predictor** in the sidebar.
2. Select a loan from the dropdown and click **Predict Target**.
3. The engine will display a suggested target settlement percentage, payout amount, lender risk category, and priority score.

### 2.6 Generate Hardship Negotiation Letters
1. Go to **Negotiate** in the sidebar.
2. Select a loan, enter your proposed settlement amount, and choose a hardship reason (e.g., job loss, medical emergency).
3. Click **Generate Letter**.
4. Review and copy the letter to send to your creditor.

---

## 3. Troubleshooting

### 1. Database Locking Error (`database is locked`)
* **Cause**: Cloud storage services (such as OneDrive or Dropbox) lock SQLite temporary files during synchronization.
* **Resolution**: The system automatically limits WAL transactions. If the error persists, move the project folder out of your cloud-synced directory (e.g., from OneDrive to a local folder like `C:\projects\`).

### 2. Connection Refused / Frontend Loading Forever
* **Cause**: The React development server is running, but the FastAPI backend is stopped or failed to start.
* **Resolution**: Ensure the terminal running `uvicorn app.main:app` is active and displays `Application startup complete.`

### 3. "Gemini AI: DISABLED (using fallback engine)"
* **Cause**: Your `GEMINI_API_KEY` in `backend/.env` is empty or invalid.
* **Resolution**: The application remains fully functional using local templates. To enable advanced AI features, configure a valid Gemini API key in your `.env` file and restart the backend.
