# Chapter 5 — System Design

This chapter describes the structural and behavioral design of the **FinRelief AI** platform. It details the system architecture, flowcharts, data flows, use cases, database tables, and API interfaces.

---

## 5.1 System Architecture

FinRelief AI is built on a decoupled, three-tier architecture:
1. **Presentation Layer (Frontend)**: A React.js single-page application (SPA) styled with vanilla CSS variables and compiled using Vite. It handles client-side routing, user forms, and state management.
2. **Application Layer (Backend API)**: A FastAPI Python web application serving as the gateway. It implements token-based authentication guards, validates schemas using Pydantic, and executes calculation algorithms.
3. **Data Layer (Storage)**: A relational SQLite database managed via SQLAlchemy Object Relational Mapper (ORM).

### Architecture Diagram
```mermaid
graph TD
    subgraph Client ["Client Presentation Tier (React SPA)"]
        UI["React Web Interface"]
        AxiosClient["Axios HTTP client"]
        AuthCtx["Auth Context (JWT state)"]
    end

    subgraph API ["Application Server Tier (FastAPI)"]
        Router["API Gateway / Router"]
        Guard["OAuth2 / JWT Auth Guard"]
        Engine["Financial & Settlement Engine"]
        Orchestrator["AI Orchestrator"]
    end

    subgraph External ["External Services"]
        Gemini["Google Gemini API (gemini-pro)"]
    end

    subgraph Data ["Data Storage Tier"]
        DB["SQLite Database (finrelief.db)"]
        ORM["SQLAlchemy ORM Models"]
    end

    UI --> AxiosClient
    AxiosClient -->|API Requests with JWT Header| Router
    Router --> Guard
    Guard --> ORM
    Router --> Engine
    Router --> Orchestrator
    Orchestrator -->|Fallback Call| Engine
    Orchestrator -->|SDK Request| Gemini
    ORM --> DB
```

---

## 5.2 Data Flow Diagrams (DFD)

### DFD Level 0 (Context Diagram)
```mermaid
graph LR
    User["User / Debtor"]
    System["FinRelief AI System"]
    Gemini["Google Gemini API"]

    User -->|1. Registration / Login Credentials| System
    User -->|2. Monthly Income & Expenses| System
    User -->|3. Loan Portfolio Records| System
    System -->|4. JWT Access Token| User
    System -->|5. Financial Health Ratios & Metrics| User
    System -->|6. Recommended Settlement Tarfets & Letters| User
    System -->|7. Anonymous Financial Context| Gemini
    Gemini -->|8. Generated Negotiation Text| System
```

### DFD Level 1 (Process Detail Diagram)
```mermaid
graph TD
    User["User"]
    DB[("SQLite Database")]
    Gemini["Gemini API"]

    subgraph Process1 ["Process 1.0: Authenticate User"]
        P1["Verify Password & Issue JWT"]
    end

    subgraph Process2 ["Process 2.0: Loan Portfolio Manager"]
        P2["Add / Edit / Delete Loan Records"]
    end

    subgraph Process3 ["Process 3.0: Financial Health Calculator"]
        P3["Compute DTI, EMIs & Health Score"]
    end

    subgraph Process4 ["Process 4.0: Settlement Predictor"]
        P4["Calculate recommended lump sum & risk priority"]
    end

    subgraph Process5 ["Process 5.0: AI Orchestrator"]
        P5["Draft negotiation strategy / letters"]
    end

    User -->|Credentials| Process1
    Process1 -->|Write User| DB
    Process1 -->|JWT Token| User

    User -->|Loan Inputs| Process2
    Process2 -->|Write Loan| DB
    Process2 -->|Refresh Portfolio| Process3

    User -->|Income / Expenses| Process3
    Process3 -->|Read Loans| DB
    Process3 -->|Write Profile| DB
    Process3 -->|Metrics Output| User

    Process2 -->|Select Loan ID| Process4
    Process4 -->|Read Profile| DB
    Process4 -->|Write Proposal| DB
    Process4 -->|Target Proposals| User

    User -->|Generate Request| Process5
    Process5 -->|Retrieve Context| DB
    Process5 -->|Prompt Payload| Gemini
    Gemini -->|Response Text| Process5
    Process5 -->|Write AI History| DB
    Process5 -->|Form Letter| User
```

---

## 5.3 Use Case Diagram & Descriptions

### Use Case Diagram
```mermaid
leftToRightDirection
actor User as "Debtor User"
actor Gemini as "Gemini API Server"

rectangle "FinRelief AI Platform" {
    usecase UC1["Register & Login Account"]
    usecase UC2["Manage Loan Records (CRUD)"]
    usecase UC3["Calculate Financial Profile"]
    usecase UC4["Predict Settlement Offer Targets"]
    usecase UC5["Generate Hardship Negotiation Letters"]
    usecase UC6["Consult AI Financial Chat Counselor"]
    usecase UC7["View AI & Settlement History Logs"]
}

User --> UC1
User --> UC2
User --> UC3
User --> UC4
User --> UC5
User --> UC6
User --> UC7

UC5 -.->|Calls| Gemini
UC6 -.->|Calls| Gemini
```

### Use Case Descriptions

#### 1. Use Case Name: Register & Login Account
* **Actor**: Debtor User.
* **Pre-conditions**: Browser connected to platform URL.
* **Post-conditions**: User receives JWT stored in localStorage; session initiated.
* **Basic Flow**:
  1. User fills out username, email, and password on Register screen.
  2. Frontend sends JSON payload to `POST /api/v1/auth/register`.
  3. Database verifies email uniqueness and hashes password.
  4. User logins at `/login` and receives JWT access token.

#### 2. Use Case Name: Manage Loan Records (CRUD)
* **Actor**: Debtor User.
* **Pre-conditions**: Authenticated session.
* **Post-conditions**: Loan data added/modified in SQLite DB.
* **Basic Flow**:
  1. User navigates to Loan Portfolio screen.
  2. Clicks "Add Loan Record", enters balance, EMI, rate, overdue months, and clicks submit.
  3. API receives data, verifies ownership, saves record, and updates user profile statistics.

#### 3. Use Case Name: Predict Settlement Offer Targets
* **Actor**: Debtor User.
* **Pre-conditions**: Registered loans and monthly income/expenses configured.
* **Post-conditions**: Target settlement records generated and saved.
* **Basic Flow**:
  1. User opens Settlement Predictor, selects a loan, and clicks "Predict Target".
  2. API calculates base percentage adjustments according to interest and overdue months.
  3. Outputs lump-sum range, priority (Low/Medium/High/Critical), and risk category.

---

## 5.4 Sequence & Activity Diagrams

### Sequence Diagram: Hardship Letter Generation (With Fallback)
```mermaid
sequenceDiagram
    autonumber
    actor User as User Browser
    participant API as FastAPI Backend
    participant DB as SQLite Database
    participant Gemini as Google Gemini API

    User->>API: POST /api/v1/ai/generate-letter (JWT, Loan details)
    Note over API: Verify User Session from JWT
    API->>DB: Query User Profile & Loan Data
    DB-->>API: Return Income, Expenses & Loan Balances
    
    alt Gemini API Key is configured and online
        API->>Gemini: generate_content(Hardship prompt with financial context)
        Note over Gemini: Run LLM model (gemini-pro)
        Gemini-->>API: Return generated negotiation text
    else Gemini API Key is missing or service times out
        Note over API: Trigger local fallback engine
        API->>API: generate_letter_fallback() with rules-based template
    end

    API->>DB: Save AI history record (request_type='letter')
    DB-->>API: Confirm database commit
    API-->>User: HTTP 200 OK (Letter text, is_fallback flag, model_used)
```

### Activity Diagram: User Financial Health Evaluation
```mermaid
stateDiagram-v2
    [*] --> InputFinancials : Enter Income & Expenses
    InputFinancials --> QueryActiveLoans : API computes EMI details
    QueryActiveLoans --> ComputeRatios : Compute EMI/Income & Debt/Income
    
    state Decision_EMI <<choice>>
    ComputeRatios --> Decision_EMI : Check EMI ratio
    
    Decision_EMI --> ApplyEMIPenalty : EMI Ratio > 30%
    Decision_EMI --> NoEMIPenalty : EMI Ratio <= 30%
    
    state Decision_Debt <<choice>>
    ApplyEMIPenalty --> Decision_Debt
    NoEMIPenalty --> Decision_Debt
    
    Decision_Debt --> ApplyDebtPenalty : Debt-to-Income > 30%
    Decision_Debt --> NoDebtPenalty : Debt-to-Income <= 30%
    
    ApplyDebtPenalty --> CalculateHealthScore
    NoDebtPenalty --> CalculateHealthScore
    
    CalculateHealthScore --> DetermineStress : Range 0 - 100
    DetermineStress --> SaveToDB : Low, Medium, High, or Critical
    SaveToDB --> [*]
```

---

## 5.5 Entity-Relationship (ER) & Database Design

### ER Diagram
```mermaid
erDiagram
    USERS {
        int id PK
        string email UK
        string hashed_password
        string full_name
        boolean is_active
        boolean is_superuser
        datetime created_at
        datetime updated_at
    }

    LOANS {
        int id PK
        int user_id FK
        string loan_type
        string lender_name
        float original_amount
        float outstanding_amount
        float interest_rate
        float emi_amount
        int tenure_months
        int overdue_months
        string status
        datetime created_at
        datetime updated_at
    }

    FINANCIAL_PROFILES {
        int id PK
        int user_id FK "Unique"
        float monthly_income
        float monthly_expenses
        float total_emi
        float total_outstanding
        float monthly_surplus
        float debt_income_ratio
        float financial_health_score
        string stress_level
        datetime updated_at
    }

    SETTLEMENT_RECORDS {
        int id PK
        int user_id FK
        int loan_id FK
        float outstanding_amount
        float recommended_percentage
        float recommended_amount
        string priority
        string risk_category
        boolean ai_generated
        text strategy_text
        datetime created_at
    }

    AI_HISTORY {
        int id PK
        int user_id FK
        string request_type
        text prompt_summary
        text response_text
        string model_used
        boolean is_fallback
        datetime created_at
    }

    USERS ||--o{ LOANS : owns
    USERS ||--|| FINANCIAL_PROFILES : has
    USERS ||--o{ SETTLEMENT_RECORDS : predicts
    USERS ||--o{ AI_HISTORY : performs
    LOANS ||--o{ SETTLEMENT_RECORDS : evaluates
```

---

## 5.6 API Architecture & Folder Structure

The API architecture leverages FastAPI's Dependency Injection (`Depends(get_db)`, `Depends(get_current_user)`) to isolate route definitions, database transactions, and security checks.

### High-level Code Layout
```
FinRelief-AI/
├── backend/                  # FastAPI Application Core
│   └── app/
│       ├── auth/             # Authentication & token verification helpers
│       ├── core/             # Logging and middleware config
│       ├── models/           # SQLAlchemy DB models mapping SQLite tables
│       ├── routers/          # API Controllers defining routes and endpoints
│       ├── schemas/          # Pydantic models for data parsing & validation
│       ├── services/         # Calculation services & Gemini API adapters
│       └── utils/            # Developer setup and test verification scripts
├── frontend/                 # React SPA Client Layout
│   └── src/
│       ├── components/       # Global UI components (Navbar, Sidebar)
│       ├── context/          # State providers (AuthContext)
│       ├── pages/            # View components (Dashboard, Settlement, AI History)
│       ├── services/         # Axios API clients
│       └── styles/           # Global styles and design variables (index.css)
```
*For a highly detailed breakdown of files and classes, refer to the [Developer Guide](file:///c:/Users/HP/OneDrive/Desktop/FinRelief-AI/Documentation/developer_guide.md).*
