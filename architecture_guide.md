# FinSight Architecture & Study Guide

## Project Overview

FinSight is a local-first personal finance dashboard designed to provide financial analytics without requiring cloud infrastructure.

Core principles:

* Local data ownership
* Simple deployment
* Fast dashboard interactions
* AI optional, not required
* Desktop-friendly architecture

---

# High-Level Architecture

```text
User
  │
  ▼
Electron
  │
  ▼
Flask Application
  │
  ├── SQLite Database
  │
  ├── Insights Engine
  │
  ├── Budget Engine
  │
  ├── Watchlist System
  │
  └── AI Summary Service
  │
  ▼
Frontend Dashboard
```

---

# Backend Architecture

## Flask

Acts as:

* API layer
* Routing layer
* Database controller
* Analytics orchestrator

Main responsibilities:

* Transaction CRUD
* CSV imports
* Budget management
* Watchlist management
* Dashboard data delivery

---

# Database Design

## Transactions

```sql
transactions
```

| Column      | Type    |
| ----------- | ------- |
| id          | INTEGER |
| amount      | REAL    |
| category    | TEXT    |
| date        | TEXT    |
| description | TEXT    |

Purpose:

Stores all imported and manually entered transactions.

---

## Stocks

```sql
stocks
```

| Column | Type    |
| ------ | ------- |
| id     | INTEGER |
| ticker | TEXT    |

Purpose:

Stores user watchlist tickers.

---

## Budgets

```sql
budgets
```

| Column        | Type    |
| ------------- | ------- |
| id            | INTEGER |
| category      | TEXT    |
| monthly_limit | REAL    |

Purpose:

Stores category spending targets.

---

# Dashboard Flow

## Load Sequence

When application loads:

1. Categories load
2. Transactions load
3. Charts render
4. Insights generate
5. Budgets calculate
6. AI summary loads
7. Watchlist loads

---

# Insights Engine

Location:

```text
services/insights.py
```

Purpose:

Generate deterministic financial observations.

---

## Calculations

### Total Spending

Calculates:

```python
sum(expenses)
```

---

### Total Income

Calculates:

```python
sum(income)
```

---

### Refund Detection

Calculates:

```python
sum(refunds)
```

---

### Category Analysis

Determines:

* Top spending category
* Lowest spending category
* Category percentages

---

### Monthly Trend Analysis

Determines:

* Highest spending month
* Spending increases
* Spending decreases
* Trend direction

---

### Recurring Expense Detection

Logic:

Group by:

```python
(description, amount)
```

Recurring if:

```python
count >= 3
```

Examples:

* Netflix
* Spotify
* Rent
* Utilities

---

# Budget Engine

Purpose:

Compare actual spending against user limits.

Process:

1. Determine latest month
2. Aggregate spending by category
3. Compare against budget targets

Thresholds:

### Safe

```text
0-79%
```

### Warning

```text
80-99%
```

### Danger

```text
100%+
```

---

# Frontend Architecture

## Dashboard Layout

```text
Stock Ribbon

Budget Ribbon

Controls
├── Category Filter
├── CSV Upload
└── Stock Entry

Charts
├── Pie Chart
└── Monthly Trend

Analysis
├── Insights
├── Transactions
└── AI Summary
```

---

# Chart System

Library:

```text
Chart.js
```

Charts:

### Pie Chart

Displays:

Category spending distribution

### Line Chart

Displays:

Monthly spending trend

---

# Watchlist System

Purpose:

Persistent stock tracking.

Flow:

```text
Add Stock
    ↓
Save SQLite
    ↓
Reload Watchlist
    ↓
Render Ribbon
```

---

# AI Integration

Provider:

```text
Ollama
```

Purpose:

Generate natural-language summaries.

Design Choice:

AI supplements analytics.

AI does NOT replace deterministic insights.

Reason:

Deterministic calculations remain reliable and consistent.

---

# Electron Architecture

Purpose:

Package FinSight as a desktop application.

Flow:

```text
Electron
   ↓
Launch Flask
   ↓
Open localhost
   ↓
Render Dashboard
```

Benefits:

* Cross-platform
* Desktop experience
* Local data storage
* Offline capable

---

# Key Lessons Learned

## Backend

* Flask routing
* REST APIs
* SQLite persistence
* Data validation

## Frontend

* Chart.js integration
* Dynamic DOM updates
* Fetch API
* Dashboard design

## Desktop

* Electron integration
* Local-first architecture

## Analytics

* Budget monitoring
* Trend analysis
* Recurring expense detection
* Financial reporting

---

# Future Versions

## Version 1.1

Potential improvements:

* PDF export
* Better stock analytics
* Improved budget management

## Version 2.0

Potential larger features:

* Net worth tracking
* Investment portfolio management
* Financial forecasting
* Goal tracking
* Multi-user support
* Cloud synchronization

---

# Final Notes

FinSight began as a simple CSV spending analyzer and evolved into a full local-first financial dashboard with budgeting, analytics, AI integration, watchlists, and desktop deployment.

The project demonstrates practical skills in:

* Python
* Flask
* SQLite
* JavaScript
* Electron
* Local AI integration
* Full-stack application design
