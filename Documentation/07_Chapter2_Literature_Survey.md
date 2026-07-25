# Chapter 2 — Literature Survey

To position **FinRelief AI** within the current landscape of financial technologies, it is essential to examine similar systems, software utilities, and commercial services. This literature survey analyzes current solutions, details their drawbacks, and highlights how FinRelief AI improves upon them.

---

## 2.1 Analysis of Existing Solutions

### 1. Static Web Calculators (e.g., NerdWallet, Bankrate)
* **Description**: These are basic web forms where users input monthly income, rent/mortgage, and monthly debt payments to calculate a simple Debt-to-Income (DTI) ratio.
* **Drawbacks**:
  * **No Storage**: Data is not saved. If the user leaves the page, the analysis is lost.
  * **No Portfolio Tracking**: They do not support a structured CRUD portfolio where multiple individual loans with interest rates, EMIs, and overdue months are tracked.
  * **No Actions**: They output a static ratio but do not recommend a settlement target, strategy, or draft formal correspondence.

### 2. Commercial Debt Settlement Companies (e.g., National Debt Relief, Freedom Debt Relief)
* **Description**: Unregulated third-party agencies that negotiate with creditors on behalf of the debtor. They require the borrower to stop paying creditors and save funds in a dedicated escrow account until a lump-sum is built.
* **Drawbacks**:
  * **Exorbitant Service Fees**: Charge between 15% and 25% of the total outstanding debt.
  * **Credit Damage**: Mandating that borrowers stop paying loans destroys their credit score, leads to late fees, and increases the likelihood of lawsuits.
  * **Lack of Transparency**: The math and negotiation algorithms used to target specific lenders are hidden.

### 3. General-Purpose LLMs (e.g., ChatGPT, Gemini web client)
* **Description**: Debtor users can prompt raw chatbots (like ChatGPT) to "write a debt settlement letter" or "give advice on credit cards."
* **Drawbacks**:
  * **No Database Integration**: The chatbot lacks context about the user's specific loan records, outstanding balances, and historical calculations. The user must manually write out all numbers in the prompt.
  * **Hallucination and Lack of Guardrails**: Raw LLMs can recommend illegal tactics or fabricate facts (e.g., advising a user that they can sue a creditor without basis).
  * **Single-Layer System**: If the API is offline or the limit is exceeded, the user receives an error and cannot get any letter or analysis.

---

## 2.2 Literature Comparison Matrix

| Feature | NerdWallet / Bankrate | Commercial DSCs | General LLMs | **FinRelief AI** |
| :--- | :--- | :--- | :--- | :--- |
| **Authentication & Profile Storage** | ❌ None | ⚠️ Agency Owned | ❌ Session-only | **✅ Secure JWT & Local SQL DB** |
| **Loan Portfolio CRUD** | ❌ None | ⚠️ Locked by Agency | ❌ None | **✅ Full CRUD (sqlite3/SQLAlchemy)** |
| **DTI & Health Score** | ✅ Basic DTI | ❌ None | ⚠️ Text-only | **✅ Structured Financial Engine** |
| **Lump-Sum Target Prediction** | ❌ None | ⚠️ Opaque | ⚠️ Text-only | **✅ Rule-based priority & risk model** |
| **Personalized Negotiation Letters** | ❌ None | ⚠️ Managed by agent | ✅ Generates text | **✅ Gemini-Pro AI letter generator** |
| **API Failure Resiliency** | ❌ N/A | ❌ N/A | ❌ Fails | **✅ Auto Rule-Based Fallback Engine** |
| **Cost** | Free | 🔴 15%–25% of debt | Free / Subscription | **✅ 100% Free & Open Source** |

---

## 2.3 Improvements Introduced by FinRelief AI

FinRelief AI improves on the reviewed systems by combining local database storage, robust financial mathematics, and natural language generation into a unified, secure platform:

1. **Integrated Context**: Instead of prompting an AI from scratch, FinRelief AI retrieves the user's actual database records (monthly income, expenses, active loans, overdue months, interest rates) and constructs precise, structured prompts for the Google Gemini API.
2. **Local Fallback Reliability**: If the Gemini API key is missing or calls fail, the system automatically redirects request processing to `fallback_engine.py`. This engine calculates rule-based strategies and builds letter templates using the same DB context, ensuring the application remains 100% functional.
3. **Structured Financial Mathematics**: Standardizes calculations for:
   * **Surplus Cash**: $\text{Income} - \text{Expenses} - \text{Total EMIs}$
   * **EMI Ratio**: $(\text{Total EMIs} / \text{Income}) \times 100$
   * **DTI Ratio**: $(\text{Total Outstanding} / \text{Annual Income}) \times 100$
   * **Health Score**: A penalized 1-100 index mapping variables to debt levels.
4. **Transparency & Security**: Open-source architecture prevents privacy leaks. The user owns their data. No commission fees are taken, removing the financial conflict of interest present in commercial debt settlement services.
