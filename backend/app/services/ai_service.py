import os
from google import genai
from google.genai.errors import APIError

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
    
    try:
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt,
        )
        return response.text
    except APIError as e:
        if e.code == 503:
            raise Exception("The AI service is currently experiencing high demand. Please wait a moment and try again.")
        elif e.code == 429:
            raise Exception("We have exceeded our AI service rate limits. Please try again shortly.")
        else:
            raise Exception(f"AI Service Error: {e.message}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred while communicating with the AI service: {str(e)}")
