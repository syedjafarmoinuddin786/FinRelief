# API Endpoint Documentation

This document describes all API endpoints implemented in the **FinRelief AI** platform. The base URL path is `/api/v1`. All requests and responses use the `application/json` content type unless specified otherwise.

---

## 1. Authentication Router (`/auth`)

### 1.1 Register User
* **Method**: `POST`
* **Route**: `/auth/register`
* **Summary**: Register a new user account.
* **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword",
    "full_name": "John Doe"
  }
  ```
* **Success Response (HTTP 201)**:
  ```json
  {
    "success": true,
    "message": "User registered successfully",
    "data": {
      "id": 1,
      "email": "user@example.com",
      "full_name": "John Doe",
      "is_active": true,
      "created_at": "2026-07-14T21:36:33"
    }
  }
  ```
* **Errors**:
  * `400 Bad Request`: `"A user with this email already exists."`

### 1.2 Login User (JSON)
* **Method**: `POST`
* **Route**: `/auth/login/json`
* **Summary**: Login using email and password via JSON payload (used by the React frontend).
* **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword"
  }
  ```
* **Success Response (HTTP 200)**:
  ```json
  {
    "success": true,
    "message": "Login successful",
    "data": {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "bearer"
    }
  }
  ```
* **Errors**:
  * `400 Bad Request`: `"Incorrect email or password"`

### 1.3 Get Current User Session
* **Method**: `GET`
* **Route**: `/auth/me`
* **Headers**: `Authorization: Bearer <JWT_TOKEN>`
* **Summary**: Returns the profile of the currently logged-in user.
* **Success Response (HTTP 200)**:
  ```json
  {
    "success": true,
    "message": "User profile retrieved successfully",
    "data": {
      "id": 1,
      "email": "user@example.com",
      "full_name": "John Doe",
      "is_active": true,
      "created_at": "2026-07-14T21:36:33"
    }
  }
  ```

---

## 2. Loan Management Router (`/loans`)
*All endpoints in this router require a valid JWT token.*

### 2.1 List All Loans
* **Method**: `GET`
* **Route**: `/loans`
* **Success Response (HTTP 200)**:
  ```json
  {
    "success": true,
    "message": "Loans retrieved successfully",
    "data": {
      "loans": [
        {
          "id": 5,
          "loan_type": "credit_card",
          "lender_name": "HDFC Bank",
          "original_amount": 50000.0,
          "outstanding_amount": 42000.0,
          "interest_rate": 36.0,
          "emi_amount": 2500.0,
          "tenure_months": 24,
          "overdue_months": 7,
          "status": "defaulted"
        }
      ],
      "total": 1
    }
  }
  ```

### 2.2 Create Loan Record
* **Method**: `POST`
* **Route**: `/loans`
* **Request Body**:
  ```json
  {
    "loan_type": "credit_card",
    "lender_name": "HDFC Bank",
    "original_amount": 50000.0,
    "outstanding_amount": 42000.0,
    "interest_rate": 36.0,
    "emi_amount": 2500.0,
    "tenure_months": 24,
    "overdue_months": 7,
    "status": "defaulted"
  }
  ```
* **Success Response (HTTP 201)**:
  ```json
  {
    "success": true,
    "message": "Loan created successfully",
    "data": {
      "id": 5,
      "user_id": 1,
      "loan_type": "credit_card",
      "lender_name": "HDFC Bank",
      "original_amount": 50000.0,
      "outstanding_amount": 42000.0,
      "interest_rate": 36.0,
      "emi_amount": 2500.0,
      "tenure_months": 24,
      "overdue_months": 7,
      "status": "defaulted"
    }
  }
  ```

### 2.3 Modify Loan Record
* **Method**: `PUT`
* **Route**: `/loans/{loan_id}`
* **Request Body**:
  ```json
  {
    "outstanding_amount": 39000.0,
    "overdue_months": 8
  }
  ```
* **Success Response (HTTP 200)**:
  ```json
  {
    "success": true,
    "message": "Loan updated successfully",
    "data": {
      "id": 5,
      "outstanding_amount": 39000.0,
      "overdue_months": 8
    }
  }
  ```

### 2.4 Delete Loan Record
* **Method**: `DELETE`
* **Route**: `/loans/{loan_id}`
* **Success Response (HTTP 200)**:
  ```json
  {
    "success": true,
    "message": "Loan deleted successfully",
    "data": null
  }
  ```

---

## 3. Financial Engine Router (`/financial`)
*All endpoints in this router require a valid JWT token.*

### 3.1 Get Financial Health Profile
* **Method**: `GET`
* **Route**: `/financial/health`
* **Success Response (HTTP 200)**:
  ```json
  {
    "success": true,
    "message": "Financial health calculated successfully",
    "data": {
      "monthly_income": 45000.0,
      "monthly_expenses": 20000.0,
      "total_emi": 2500.0,
      "total_outstanding": 42000.0,
      "monthly_surplus": 22500.0,
      "emi_ratio": 5.56,
      "debt_income_ratio": 7.78,
      "financial_health_score": 100.0,
      "stress_level": "Low"
    }
  }
  ```

### 3.2 Update Income & Expenses
* **Method**: `POST`
* **Route**: `/financial/calculate`
* **Request Body**:
  ```json
  {
    "monthly_income": 45000.0,
    "monthly_expenses": 20000.0
  }
  ```
* **Success Response (HTTP 200)**: Returns the updated Financial Profile JSON object.

---

## 4. Settlement Engine Router (`/settlement`)
*All endpoints in this router require a valid JWT token.*

### 4.1 Predict Settlement Payout
* **Method**: `POST`
* **Route**: `/settlement/predict`
* **Request Body**:
  ```json
  {
    "loan_id": 5
  }
  ```
* **Success Response (HTTP 200)**:
  ```json
  {
    "success": true,
    "message": "Settlement recommendation generated successfully",
    "data": {
      "loan_id": 5,
      "loan_type": "credit_card",
      "lender_name": "HDFC Bank",
      "outstanding_amount": 42000.0,
      "recommended_percentage": 45.0,
      "recommended_amount": 18900.0,
      "priority": "High",
      "risk_category": "High",
      "strategy_text": "Based on the analysis of your credit_card loan with HDFC Bank...",
      "ai_generated": false,
      "financial_health": "Low"
    }
  }
  ```

---

## 5. AI Engine Router (`/ai`)
*All endpoints in this router require a valid JWT token.*

### 5.1 Generate Negotiation Strategy
* **Method**: `POST`
* **Route**: `/ai/generate-strategy`
* **Request Body**:
  ```json
  {
    "monthly_income": 45000.0,
    "monthly_expenses": 20000.0,
    "outstanding_amount": 42000.0,
    "loan_type": "credit_card",
    "overdue_months": 7,
    "interest_rate": 36.0,
    "lender_name": "HDFC Bank"
  }
  ```
* **Success Response (HTTP 200)**:
  ```json
  {
    "success": true,
    "message": "Strategy generated successfully",
    "data": {
      "strategy": "=== FINRELIEF AI — NEGOTIATION STRATEGY... \n...",
      "is_fallback": false,
      "model_used": "gemini-pro"
    }
  }
  ```

### 5.2 Generate Hardship Negotiation Letter
* **Method**: `POST`
* **Route**: `/ai/generate-letter`
* **Request Body**:
  ```json
  {
    "borrower_name": "John Doe",
    "lender_name": "HDFC Bank",
    "loan_type": "credit_card",
    "outstanding_amount": 42000.0,
    "proposed_settlement_amount": 18900.0,
    "overdue_months": 7,
    "reason": "medical emergency in family"
  }
  ```
* **Success Response (HTTP 200)**:
  ```json
  {
    "success": true,
    "message": "Negotiation letter generated successfully",
    "data": {
      "letter": "Date: [Current Date]\n\nTo,\nThe Collections Manager\nHDFC Bank\n...",
      "is_fallback": true,
      "model_used": "fallback"
    }
  }
  ```

### 5.3 Chat with AI counselor
* **Method**: `POST`
* **Route**: `/ai/chat`
* **Request Body**:
  ```json
  {
    "message": "How will settling my HDFC credit card affect my credit score?",
    "monthly_income": 45000.0,
    "monthly_expenses": 20000.0,
    "total_outstanding": 42000.0
  }
  ```
* **Success Response (HTTP 200)**:
  ```json
  {
    "success": true,
    "message": "Chat reply generated successfully",
    "data": {
      "reply": "FinRelief AI Counselor:\n\nSettling your account will stay on your credit bureau report for up to 7 years...",
      "is_fallback": false,
      "model_used": "gemini-pro"
    }
  }
  ```

---

## 6. Audit & History Router (`/history`)
*Requires valid JWT token.*

### 6.1 Get AI Activity Logs
* **Method**: `GET`
* **Route**: `/history/ai`
* **Query Parameters**:
  * `skip` (default: `0`): Records to skip.
  * `limit` (default: `50`): Maximum records to return.
* **Success Response (HTTP 200)**:
  ```json
  {
    "success": true,
    "message": "AI history retrieved successfully",
    "data": {
      "records": [
        {
          "id": 12,
          "request_type": "letter",
          "prompt_summary": "Letter: John Doe to HDFC Bank, ₹42,000 → ₹18,900",
          "response_text": "...",
          "model_used": "fallback",
          "is_fallback": true,
          "created_at": "2026-07-14T21:36:33"
        }
      ],
      "total": 1
    }
  }
  ```
