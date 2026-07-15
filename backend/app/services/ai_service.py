import os
from google import genai

def analyze_financials(total_debt: float, monthly_income: float, monthly_expenses: float) -> str:
    # Initialize the client. It automatically picks up GEMINI_API_KEY from the environment.
    client = genai.Client()
    
    prompt = f"""
    You are an expert, empathetic financial advisor specialized in debt relief.
    A user has provided the following financial snapshot:
    - Total Debt: ${total_debt}
    - Monthly Income: ${monthly_income}
    - Monthly Expenses: ${monthly_expenses}
    
    Calculate their monthly disposable income. Then, provide a concise, actionable, and encouraging 3-step plan 
    to help them manage and reduce their debt. Return the response in Markdown format.
    """
    
    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=prompt,
    )
    return response.text
