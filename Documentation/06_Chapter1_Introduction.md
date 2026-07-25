# Chapter 1 — Introduction

## 1.1 Background
In the modern economic landscape, consumer credit has become highly accessible. Microloans, credit cards, BNPL (Buy Now Pay Later) schemes, and personal retail loans have expanded consumer purchasing power. However, this accessibility has also led to a sharp increase in personal debt accumulation. Many individuals live paycheck to paycheck, and minor disruptions (such as medical emergencies, job losses, or salary cuts) can push a borrower into default. 

Once in default, individuals face high interest penalties, compounding fees, and aggressive collection efforts. Understanding how to manage, restructure, or settle outstanding debts is a complex process. Borrowers often lack the financial literacy or support to navigate these scenarios independently.

---

## 1.2 Problem Statement
Struggling borrowers face a multi-faceted problem when dealing with outstanding debts:
1. **Lack of Analysis Tools**: Users do not have simple, secure tools to evaluate their Debt-to-Income (DTI) ratio, monthly surplus, and overall debt stress level.
2. **Opaque Settlement Thresholds**: Lenders have varying criteria for accepting a "one-time settlement" (OTS). Borrowers do not know what range (e.g., 40% vs 80%) is a realistic target based on their loan type, interest rates, and overdue duration.
3. **Drafting Correspondence**: Writing professional hardship and negotiation letters is difficult. Informal letters are often ignored, while hiring legal professionals or agencies is too expensive.
4. **Dependence on Third-Party Agencies**: Debt relief companies charge upfront percentages of the debt saved, and some operate with predatory terms.
5. **Lack of Conversational Advice**: Getting immediate, basic guidance on credit scores, budgeting, and settlement processes without sharing data with aggressive agents is rare.

---

## 1.3 Existing System
Historically, the debt settlement system relies on manual intervention:
* **Manual Tracking**: Users list their debts in paper journals or basic Excel sheets without automatic ratio calculations or financial priority rankings.
* **Third-Party Debt Settlement Companies (DSCs)**: DSCs negotiate on behalf of the debtor. They require the borrower to stop paying creditors and save funds in a dedicated account. This ruins the borrower's credit score and leads to lawsuits.
* **Direct Manual Negotiation**: The borrower contacts the creditor directly. They write basic, unstructured emails, often proposing unrealistic targets, leading to rejection.

---

## 1.4 Drawbacks of Existing Systems
* **High Fees**: Debt settlement companies charge 15% to 25% of the total enrolled debt as service fees.
* **Aggressive Deterioration of Credit**: DSCs push users into default even if they could afford structured EMI payments, destroying their credit history.
* **No Local Fallback**: Automated tools are completely web-dependent. If the server or API is down, the user has zero resources.
* **Privacy Concerns**: Online debt counselors require sharing personal identification details, leading to data leaks or unsolicited sales calls.
* **One-Size-Fits-All Logic**: Basic online calculators ignore specific lender risks, interest rates, and overdue periods.

---

## 1.5 Proposed System
**FinRelief AI** is an autonomous, secure, and user-centric platform that puts debt evaluation, prioritization, and negotiation tools directly into the borrower's hands.

The proposed system addresses the drawbacks of existing methods by providing:
1. **Secure Local Dashboard**: A fully private, self-service dashboard to manage a loan portfolio (original amounts, EMIs, interest rates, overdue periods).
2. **Integrated Algorithmic Engine**: Local calculation services that automatically compile DTI ratios, monthly surplus, and overall health scores.
3. **Dual-Model Negotiation Engine**: A smart AI engine powered by Google Gemini API to write personalized hardship letters and strategies. It includes an embedded rule-based fallback service that operates locally if the API is offline.
4. **Immediate AI counselor**: An interactive chatbot helper on the dashboard that answers questions regarding budgeting, credit bureaus, and negotiation tips.
5. **No Data Sharing**: Run completely locally or on private user servers, preventing third-party tracking.

---

## 1.6 Objectives
* Develop a secure, interactive full-stack web application.
* Implement JWT-based user authentication to protect financial data.
* Provide a full CRUD loan portfolio manager.
* Calculate financial health metrics (DTI, EMI-to-Income, Cash Surplus, Health Score).
* Build a lender risk classifier and settlement target predictor.
* Integrate Google Gemini API for drafting customized hardship letters and negotiation strategies.
* Implement a robust, rules-based fallback engine for offline or API-less execution.
* Store AI interactions and settlement history logs in a local SQLite database.

---

## 1.7 Scope
The scope of **FinRelief AI** is to serve as a personal financial counseling and debt negotiation helper. The system provides:
* **Analysis**: Real-time evaluation of a user's financial profile.
* **Strategy Formulation**: Recommending settlement amounts and strategic timelines.
* **Communication Generation**: Drafting letters for one-time settlements.
* **Interactive Counseling**: Explaining concepts of budgeting and credit bureaus.

*Out of Scope*: The application does not process payments to lenders, does not submit disputes to credit bureaus, and does not serve as a legal representative in court.

---

## 1.8 Project Overview
FinRelief AI is organized into a modular full-stack layout:
* **Frontend SPA**: React.js client compiled using Vite. Uses a sleek, dark glassmorphic design system using CSS variables, responsive grids, and clean component separation.
* **Backend API Gateway**: FastAPI python framework implementing routers for security, loans CRUD, calculations, predictions, AI generations, and history logs.
* **Data Access Layer**: SQLite database accessed via SQLAlchemy ORM, representing users, loans, profiles, settlement proposals, and history records.
