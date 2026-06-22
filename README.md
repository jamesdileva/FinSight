# FinSight

A local-first personal finance dashboard built with Flask, SQLite, Chart.js, Electron, and Ollama.

FinSight helps users track spending, analyze financial trends, monitor budgets, detect recurring expenses, and generate AI-powered financial summaries while keeping data stored locally on their machine.

---

## Features

### Financial Dashboard

* Monthly spending trend chart
* Category spending breakdown
* Financial insights engine
* AI-generated financial summaries

### Transaction Management

* CSV transaction imports
* Manual transaction entry
* Edit existing transactions
* Delete transactions
* Search and filter transactions

### Budget Tracking

* Create category budgets
* Visual budget progress indicators
* Overspending alerts
* Budget monitoring by category

### Recurring Expense Detection

Automatically identifies recurring expenses such as:

* Subscriptions
* Rent
* Utilities
* Memberships

### Stock Watchlist

* Add stock tickers
* Remove tickers
* Persistent watchlist
* Dashboard ribbon display

### Local AI Analysis

Optional AI summaries powered by Ollama.

Supported local models include:

* Llama 3
* Gemma
* Other Ollama-compatible models

---

## Technology Stack

### Backend

* Python
* Flask
* SQLite

### Frontend

* HTML
* CSS
* JavaScript
* Chart.js

### Desktop Application

* Electron

### AI

* Ollama
* Local LLMs

---

## Screenshots

Add screenshots here.

Example:

* Dashboard
* Budget Tracking
* Transaction Management
* AI Summary
* Stock Watchlist

---

## Installation

### Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/FinSight.git
cd FinSight
```

### Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Run Application

```bash
python app.py
```

Open:

http://127.0.0.1:5000

---

## Optional AI Setup

Install Ollama:

https://ollama.com

Download a model:

```bash
ollama pull llama3.1:8b
```

Run:

```bash
ollama serve
```

AI summaries will automatically become available.

---

## Electron Desktop Version

Install dependencies:

```bash
npm install
```

Run Electron:

```bash
npm start
```

---

## Project Structure

```text
FinSight/
│
├── app.py
├── finance.db
├── requirements.txt
│
├── services/
│   └── insights.py
│
├── templates/
│   └── index.html
│
├── static/
│
├── electron/
│
└── README.md
```

---

## Future Roadmap

Potential future enhancements:

* PDF report exports
* Net worth tracking
* Investment portfolio analytics
* Multi-user support
* Budget forecasting
* Financial goal planning
* Custom dashboard widgets
* Enhanced stock analytics
* Cloud synchronization
* Automated transaction categorization

---

## License

MIT License

---

## Author

James DiLeva

Built as a portfolio and learning project focused on local-first financial analytics and desktop application development.
