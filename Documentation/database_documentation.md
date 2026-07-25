# Database Documentation

This document describes the database design, schema, tables, relationships, and constraints implemented in **FinRelief AI** using SQLite and SQLAlchemy ORM.

---

## 1. Relational Entity Mapping

The database schema consists of 5 tables:
1. `users`: Stores user authentication details and system flags.
2. `loans`: Tracks individual loan accounts, balances, and interest rates.
3. `financial_profiles`: Holds compiled DTI values, surplus cash, and stress levels (1:1 with user).
4. `settlement_records`: Caches predicted one-time settlement options and priority scores.
5. `ai_history`: Records prompts and responses for audit trails and chat logs.

---

## 2. Table Specifications

### 2.1 `users` Table
Stores user credentials and metadata.

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY`, `AUTOINCREMENT` | Unique identifier. |
| `email` | `VARCHAR` | `UNIQUE`, `INDEX`, `NOT NULL` | User email address. |
| `hashed_password` | `VARCHAR` | `NOT NULL` | Bcrypt hashed password. |
| `full_name` | `VARCHAR` | `NULLABLE` | Optional user name. |
| `is_active` | `BOOLEAN` | `DEFAULT True` | User active status. |
| `is_superuser` | `BOOLEAN` | `DEFAULT False` | Administrator flag. |
| `created_at` | `DATETIME` | `DEFAULT utcnow` | Registration timestamp. |
| `updated_at` | `DATETIME` | `DEFAULT utcnow` | Last update timestamp. |

### 2.2 `loans` Table
Tracks user loan details.

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY`, `AUTOINCREMENT` | Unique identifier. |
| `user_id` | `INTEGER` | `FOREIGN KEY(users.id)`, `INDEX`, `NOT NULL` | Link to the loan owner. |
| `loan_type` | `VARCHAR` | `NOT NULL` | Types: `personal`, `home`, `auto`, `credit_card`, `student`, `business`. |
| `lender_name` | `VARCHAR` | `NOT NULL` | Bank/Creditor name. |
| `original_amount` | `FLOAT` | `NOT NULL` | Loan principal amount. |
| `outstanding_amount` | `FLOAT` | `NOT NULL` | Current outstanding debt. |
| `interest_rate` | `FLOAT` | `NOT NULL` | Annual percentage rate (APR). |
| `emi_amount` | `FLOAT` | `DEFAULT 0.0` | Monthly payment amount. |
| `tenure_months` | `INTEGER` | `DEFAULT 0` | Total tenure of the loan. |
| `overdue_months` | `INTEGER` | `DEFAULT 0` | Months unpaid. |
| `status` | `VARCHAR` | `DEFAULT "active"` | Options: `active`, `closed`, `settled`, `defaulted`. |
| `created_at` | `DATETIME` | `DEFAULT utcnow` | Record creation date. |
| `updated_at` | `DATETIME` | `DEFAULT utcnow` | Last update timestamp. |

### 2.3 `financial_profiles` Table
Stores calculated budget ratios and health scores.

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY`, `AUTOINCREMENT` | Unique identifier. |
| `user_id` | `INTEGER` | `FOREIGN KEY(users.id)`, `UNIQUE`, `INDEX`, `NOT NULL` | Link to the user (1:1 relation). |
| `monthly_income` | `FLOAT` | `DEFAULT 0.0` | User monthly income. |
| `monthly_expenses` | `FLOAT` | `DEFAULT 0.0` | User monthly expenses. |
| `total_emi` | `FLOAT` | `DEFAULT 0.0` | Combined active EMI payments. |
| `total_outstanding` | `FLOAT` | `DEFAULT 0.0` | Total outstanding debt. |
| `monthly_surplus` | `FLOAT` | `DEFAULT 0.0` | Surplus cash: $\text{Income} - \text{Expenses} - \text{EMI}$. |
| `debt_income_ratio` | `FLOAT` | `DEFAULT 0.0` | Debt-to-income ratio (DTI). |
| `financial_health_score` | `FLOAT` | `DEFAULT 0.0` | Performance index (1–100). |
| `stress_level` | `VARCHAR` | `DEFAULT "Low"` | Classifications: `Low`, `Medium`, `High`, `Critical`. |
| `updated_at` | `DATETIME` | `DEFAULT utcnow` | Last update timestamp. |

### 2.4 `settlement_records` Table
Caches recommended settlement targets.

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY`, `AUTOINCREMENT` | Unique identifier. |
| `user_id` | `INTEGER` | `FOREIGN KEY(users.id)`, `INDEX`, `NOT NULL` | Link to user. |
| `loan_id` | `INTEGER` | `FOREIGN KEY(loans.id)`, `INDEX`, `NOT NULL` | Link to the loan. |
| `outstanding_amount` | `FLOAT` | `NOT NULL` | Outstanding amount at prediction. |
| `recommended_percentage` | `FLOAT` | `NOT NULL` | Suggested payment percentage. |
| `recommended_amount` | `FLOAT` | `NOT NULL` | Suggested lump-sum payment. |
| `priority` | `VARCHAR` | `NOT NULL` | Payout priority: `Low`, `Medium`, `High`, `Critical`. |
| `risk_category` | `VARCHAR` | `NOT NULL` | Lender risk: `Low`, `Moderate`, `High`, `Critical`. |
| `ai_generated` | `BOOLEAN` | `DEFAULT False` | Indicates if created by AI model. |
| `strategy_text` | `TEXT` | `NULLABLE` | Negotiation summary strategy. |
| `created_at` | `DATETIME` | `DEFAULT utcnow` | Prediction timestamp. |

### 2.5 `ai_history` Table
Stores logs of AI interactions.

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY`, `AUTOINCREMENT` | Unique identifier. |
| `user_id` | `INTEGER` | `FOREIGN KEY(users.id)`, `INDEX`, `NOT NULL` | Link to user. |
| `request_type` | `VARCHAR` | `NOT NULL` | Types: `strategy`, `letter`, `chat`. |
| `prompt_summary` | `TEXT` | `NOT NULL` | Brief description of the prompt. |
| `response_text` | `TEXT` | `NOT NULL` | Full output text. |
| `model_used` | `VARCHAR` | `DEFAULT "fallback"` | Model name (e.g., `gemini-pro`, `fallback`). |
| `is_fallback` | `BOOLEAN` | `DEFAULT True` | Indicates if fallback engine was used. |
| `created_at` | `DATETIME` | `DEFAULT utcnow` | Generation timestamp. |

---

## 3. Key Relationships and Cascades

* **User Ownership**:
  `users` tables acts as the parent. Foreign key definitions in `loans`, `financial_profiles`, `settlement_records`, and `ai_history` are configured with `ondelete="CASCADE"`. Deleting a user profile automatically deletes all associated records, keeping the database clean.
* **1:1 Constraint on Profile**:
  `users` has a one-to-one relationship with `financial_profiles` using `uselist=False`, ensuring each user has a single active financial profile.
* **Loan and Settlement Mapping**:
  Deleting a loan record cascades and removes any associated settlement prediction records in `settlement_records`, preventing orphan data.
* **Transactional Security**:
  All database transactions are handled within a context-managed session factory `get_db()`. If an error occurs, changes are rolled back to prevent database corruption.
