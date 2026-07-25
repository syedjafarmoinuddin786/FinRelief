# FinRelief: AI-Powered Debt Recovery Platform 🚀

FinRelief is a comprehensive, full-stack financial advisory and debt management platform designed to help users climb out of debt using AI. Built with a strict adherence to **OWASP Top 10:2025 security principles** and a modern **Glassmorphism design system**, this platform acts as an intelligent, empathetic financial advisor for individuals experiencing debt stress.

---

## 👨‍💻 Developer & Author

**Syed Jafar Moinuddin**
*4th Year Computer Science Graduate*
*Vishnu Institute of Technology, Bhimavaram*

This project was developed by Syed Jafar Moinuddin as a capstone-level demonstration of full-stack engineering, AI integration, and enterprise-grade security practices. 

---

## 🌟 Key Features 

- **Advanced AI Chatbot**: Real-time empathetic financial advice powered by Google Gemini.
- **Payoff Planner (Snowball vs. Avalanche)**: Simulates debt payoff strategies based on the user's actual deterministic monthly surplus and EMI data.
- **AI Settlement & Negotiation Letter Generator**: Generates customized, tone-specific (Professional, Firm, Conciliatory) negotiation letters to send to lenders.
- **Interactive Dashboard**: Track active and settled loans, total debt, and financial health via real-time `Chart.js` graphs.
- **FDCPA Rights Library**: A built-in educational resource teaching users about their rights under the Fair Debt Collection Practices Act.
- **Enterprise Security**: 
  - JWT Authentication & `bcrypt` password hashing.
  - Rate Limiting (`slowapi`) against brute-force attacks.
  - Google Authenticator (TOTP) 2FA integration.
  - Strict CORS policies, HSTS, and XSS sanitization (`DOMPurify`).

## 🛠 Tech Stack

- **Backend**: Python 3.10+, FastAPI, SQLAlchemy, SQLite, Pytest
- **Frontend**: HTML5, Vanilla JavaScript, CSS3 (Custom Glassmorphism, CSS Grid, Floating Animations)
- **AI Integration**: Google Cloud Generative AI (`google-genai` SDK)

---

## 🚀 Setup Instructions

**1. Clone the repository**
```bash
git clone https://github.com/syedjafarmoinuddin786/FinRelief.git
cd FinRelief
```

**2. Backend Setup**
```bash
cd backend
python -m venv .venv
# Activate virtual environment
# Windows: .venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate

pip install -r requirements.txt
```

**3. Configure Environment Variables**
In the `backend` folder, create a file named `.env` and add your required keys:
```env
GEMINI_API_KEY=your_gemini_api_key_here
JWT_SECRET=your_super_secret_jwt_key
FRONTEND_URL=http://localhost:3000,http://127.0.0.1:3000
```

**4. Start the Servers**
You can use the provided batch script to start both servers at once on Windows:
```cmd
start_finrelief.bat
```
*Alternatively, run them manually:*
- **Backend:** `uvicorn app.main:app --host 127.0.0.1 --port 8000`
- **Frontend:** `python -m http.server 3000` (run from inside the `frontend` folder)

**5. Access the App**
Open your browser and navigate to: http://localhost:3000

---

## 🧪 Testing

This project includes a comprehensive Pytest suite that mocks the Gemini API to allow offline testing of the core logic and endpoints.

```bash
cd backend
pytest tests/
```

---

## 🔒 Evaluator Notes
- **Security First**: `.env` and `finrelief.db` are strictly excluded via `.gitignore`. You **must** supply your own `.env` file to test the AI features.
- **Testing**: The Pytest suite fully tests auth, loan CRUD, and AI generation endpoints.
- **Admin Access**: Register an account with the email `admin@example.com` to automatically unlock the exclusive Admin Panel in the navigation bar!