## Smart Receivables Risk & Collection Control

Identify risky receivables earlier and help financial teams decide which money to pursue today.
A focused B2B SaaS application that analyzes outstanding receivables, detects collection risk, and turns financial data into actionable collection priorities.

## The Problem
Having a list of outstanding invoices is not the same as knowing where the real collection risk is.
Financial teams need to quickly understand:
- Which customers are becoming risky?
- How much money is exposed?
- Which receivables are already overdue?
- Which customers require attention today?
- Smart Receivables Risk & Collection Control is designed to answer these questions without replacing the company's existing accounting or ERP system.

## What It Does
The application takes receivables data from Excel/CSV and transforms it into a financial risk and collection view.

Receivables Data
       ↓
Data Processing
       ↓
Risk Analysis
       ↓
Customer Risk
       ↓
Collection Priorities


## Key Features

## 📥 Receivables Import
Import existing receivables data from Excel/CSV without changing the company's current financial workflow.

## ⚠️ Customer Risk Scoring
Each customer receives a risk score based on factors such as:
- Overdue days
- Outstanding debt

## 🔎 Explainable Risk
- The system does not only provide a score.
- It also explains why a customer is considered risky, making the result easier for financial teams to understand and act on.

## 📊 Financial Dashboard
A centralized view of:
- Total receivables
- Overdue receivables
- Overdue invoices
- High-risk customers
- Collection priorities

## 🎯 Today's Collection Priorities
Instead of showing every overdue invoice equally, the system helps identify which customers deserve attention first based on their financial exposure and risk.

## 👤 Customer Risk Detail
A dedicated view for each customer showing:
- Risk score
- Risk level
- Risk reasons
- Outstanding debt
- Open invoices

## Risk Engine
The current MVP uses a transparent rule-based scoring engine.
The main inputs are:
- Overdue Days
- Outstanding Debt

| Score | Risk     |
|------:|----------|
| 0–30  | Low      |
| 31–60 | Medium   |
| 61–80 | High     |
| 81–100| Critical |

The initial rule-based approach keeps the system predictable and explainable.

More advanced risk models can be introduced later as real-world data becomes available.

## Product Architecture
The application is built as a modular Django web application.

Excel / CSV
     │
     ▼
  imports
     │
     ▼
customers + invoices
     │
     ▼
    risk
     │
     ├── Risk Score
     ├── Risk Level
     └── Risk Reasons
     │
     ▼
 dashboard
     │
     ├── Financial Overview
     ├── High-Risk Customers
     └── Today's Actions
     │
     ▼
Customer Risk Detail


## Project Structure

receivables/
├── companies/       # Company and user-company relationships
├── config/          # Django configuration
├── customers/       # Customer management
├── dashboard/       # Financial dashboard and collection priorities
├── demo_data/       # Synthetic demo data
├── imports/         # Excel/CSV import and processing
├── invoices/        # Invoices and payments
├── risk/            # Risk models and scoring engine
├── static/          # Static assets
├── templates/       # Django templates
├── manage.py
├── requirements.txt
└── README.md

## Tech Stack

## Backend
- Python
- Django

## Database
- PostgreSQL

## Data Processing
- pandas
- openpyxl

## Frontend
- Django Templates
- HTML
- CSS

## Development
- Git
- GitHub

## Demo Data
The project includes synthetic receivables data for demonstrating the complete workflow.

The demo data is fictional and does not represent real companies, customers, or financial records.

## MVP Status
The current MVP includes:
- [x] Excel/CSV import
- [x] Customer management
- [x] Invoice management
- [x] Receivables analysis
- [x] Customer risk scoring
- [x] Risk levels
- [x] Explainable risk reasons
- [x] Financial dashboard
- [x] High-risk customer monitoring
- [x] Customer risk detail
- [x] Overdue receivables
- [x] Today's collection priorities
- [x] Authentication
- [x] Company-level data isolation
- [x] PostgreSQL support
- [x] Synthetic demo data

The core workflow is implemented, while the product remains under active development.

## Direction
The product is intentionally focused on one problem:
- Receivables risk and collection prioritization.
It is not intended to replace accounting, ERP, CRM, invoicing, or payment systems.

The goal is to provide a focused intelligence layer that helps financial teams identify collection risk earlier and act on the right receivables first.

## Status

## MVP — Active Development
The current version focuses on establishing a reliable workflow from:

Financial Data
      ↓
Risk Analysis
      ↓
Financial Visibility
      ↓
Collection Action

## License
This project is currently private and is not licensed for redistribution.
