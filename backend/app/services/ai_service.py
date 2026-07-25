import os
from google import genai
from google.genai import types

# A10: Do not proceed if Gemini is missing.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("CRITICAL ERROR: GEMINI_API_KEY environment variable is not set!")

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
client = genai.Client(api_key=GEMINI_API_KEY)

# --------------------------
# Deterministic Financial Math (Scenario 1)
# --------------------------
def compute_financial_metrics(outstanding_amount: float, monthly_income: float, monthly_expenses: float, loan_emi: float, overdue_months: int):
    # A10: Guard against division by zero
    if monthly_income <= 0:
        raise ValueError("Monthly income must be greater than 0")

    emi_ratio = round(loan_emi / monthly_income, 4)
    dti_ratio = round(outstanding_amount / (monthly_income * 12), 4)
    monthly_surplus = round(monthly_income - monthly_expenses - loan_emi, 2)
    
    def stress_level(emi, dti, overdue):
        if overdue >= 6 or dti >= 0.6 or emi >= 0.6:
            return "Critical"
        if overdue >= 3 or dti >= 0.4 or emi >= 0.4:
            return "High"
        if dti >= 0.25 or emi >= 0.25:
            return "Medium"
        return "Low"

    risk_category = stress_level(emi_ratio, dti_ratio, overdue_months)
    
    SETTLEMENT_PCT_BY_RISK = {"Low": 0.70, "Medium": 0.55, "High": 0.45, "Critical": 0.35}
    suggested_settlement = round(outstanding_amount * SETTLEMENT_PCT_BY_RISK[risk_category], 2)
    
    return {
        "emi_ratio": emi_ratio,
        "dti_ratio": dti_ratio,
        "monthly_surplus": monthly_surplus,
        "stress_level": risk_category, # risk_category mirrors stress_level
        "suggested_settlement": suggested_settlement
    }

# --------------------------
# AI Generations
# --------------------------
def generate_settlement_recommendation(
    lender_name: str, loan_type: str, outstanding_amount: float, overdue_months: int,
    emi_ratio: float, dti_ratio: float, monthly_surplus: float, stress_level: str, suggested_settlement: float
) -> str:
    prompt = f"""You are an elite financial strategist and empathetic debt recovery specialist.
A borrower is seeking advanced guidance on restructuring their debt.

Borrower Profile:
- Lender: {lender_name}
- Loan Type: {loan_type}
- Outstanding Amount: ${outstanding_amount}
- Overdue: {overdue_months} month(s)
- EMI-to-Income Ratio: {emi_ratio}
- Debt-to-Income Ratio: {dti_ratio}
- Monthly Surplus: ${monthly_surplus}
- Debt Stress Level: {stress_level}
- Calculated Settlement Opportunity: ${suggested_settlement}

Provide a comprehensive, highly-detailed response in Markdown with exactly these sections:
### 1. 📊 Debt Stress Analysis
Deep dive into what their {stress_level} stress level implies for their credit score and psychological well-being.
### 2. 💡 Financial Health & Ratios
Explain the EMI and DTI ratios in layman's terms. Are they above industry thresholds (e.g. 40% DTI)?
### 3. 🎯 Advanced Restructuring Strategy
Provide 2-3 specific options (e.g., Debt Snowball, Avalanche, Hardship Programs, or Settlement) based on their surplus of ${monthly_surplus}.
### 4. 🤝 Settlement Recommendation
Detail exactly why a settlement of ${suggested_settlement} is realistic for {lender_name} and outline the next immediate steps.

Keep it empathetic, professional, and actionable."""

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print(f"Gemini API Warning: {str(e)}. Using mock fallback.")
        return f"""### 1. 📊 Debt Stress Analysis
Your debt stress level is **{stress_level}**. This indicates that your current debt obligations are significantly impacting your financial stability and potentially your credit health. It's completely normal to feel overwhelmed, but recognizing the situation is the first step to recovery.

### 2. 💡 Financial Health & Ratios
Your EMI-to-Income ratio is {emi_ratio} and Debt-to-Income ratio is {dti_ratio}. Generally, a DTI over 0.40 is considered a high burden. With a monthly surplus of ${monthly_surplus}, you have some flexibility to restructure.

### 3. 🎯 Advanced Restructuring Strategy
Given your surplus, you have a few options:
*   **Hardship Program:** Request a temporary reduction in interest from {lender_name}.
*   **Targeted Paydown:** Allocate $50 of your surplus specifically to the principal of this {loan_type}.
*   **Lump Sum Settlement:** Use savings to offer a one-time reduced payment to close the account.

### 4. 🤝 Settlement Recommendation
We recommend proposing a settlement of **${suggested_settlement}**. Given your {stress_level} stress level and {overdue_months} months overdue, lenders are often willing to negotiate. Your next step is to generate a formal negotiation letter using our AI tool."""


def generate_negotiation_letter(
    borrower_name: str, lender_name: str, loan_type: str, outstanding_amount: float,
    overdue_months: int, monthly_surplus: float, suggested_settlement: float, tone: str = "professional"
) -> dict:
    prompt = f"""You are an expert debt-negotiation consultant. Draft a {tone}, respectful settlement negotiation letter a borrower can send to their lender.

Borrower: {borrower_name}
Lender: {lender_name}
Loan Type: {loan_type}
Outstanding Amount: ${outstanding_amount}
Months Overdue: {overdue_months}
Borrower's Monthly Surplus: ${monthly_surplus}
Proposed Settlement Amount: ${suggested_settlement}

Return your response as two clearly labeled Markdown sections:

## Strategy
2-3 sentences on the negotiation approach and why this settlement figure is reasonable given the borrower's situation.

## Letter
The full negotiation letter, addressed to {lender_name}, written in first person as the borrower, professional in tone, proposing the settlement amount above (or a structured payment plan as an alternative), and requesting a response within 14 business days. Write it as a plain formatted letter with a greeting, body, and sign-off — no markdown headers inside the letter itself."""

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )
        
        full_text = response.text
        strategy = ""
        letter = full_text
        
        if "## Strategy" in full_text and "## Letter" in full_text:
            parts = full_text.split("## Letter")
            strategy_part = parts[0].replace("## Strategy", "").strip()
            letter_part = parts[1].strip()
            strategy = strategy_part
            letter = letter_part
            
        return {"strategy": strategy, "letter": letter}
    except Exception as e:
        print(f"Gemini API Warning: {str(e)}. Using mock fallback.")
        return {
            "strategy": f"Because your stress level indicates financial hardship, we will use a {tone} approach to emphasize your limited ${monthly_surplus} surplus and propose a final settlement of ${suggested_settlement}.",
            "letter": f"Dear {lender_name},\n\nI am writing to you today to discuss my outstanding loan ({loan_type}). Unfortunately, I am currently experiencing financial hardship.\n\nAfter reviewing my finances, I am unable to maintain the current payments. However, in an effort to resolve this debt, I can offer a one-time lump sum settlement of ${suggested_settlement} to close this account in full.\n\nPlease let me know if this is acceptable. I look forward to resolving this matter amicably.\n\nSincerely,\n{borrower_name}"
        }

def chat_with_advisor(message: str, user_name: str, total_debt: float) -> str:
    prompt = f"""You are an empathetic, expert AI financial advisor named 'FinRelief Advisor'. 
You are chatting with {user_name}, whose current total debt is ${total_debt}.
Provide a helpful, concise, and actionable response to their message: "{message}"
Use Markdown for formatting if necessary, but keep the response conversational and suitable for a chat interface."""
    
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print(f"Gemini API Warning: {str(e)}. Using mock fallback.")
        return f"Hello {user_name}! As your advisor, I recommend looking closely at your ${total_debt} debt and prioritizing the highest interest loans first. How else can I assist you today?"

