#  FinSight — Personal Finance Dashboard (SaaS-Style)

## Overview

**FinSight** is a full-stack personal finance dashboard designed to replicate the look and feel of a modern SaaS product. It allows users to track expenses, visualize spending patterns, generate insights, and monitor stock performance — all within a clean, responsive UI.

This project focuses not just on functionality, but on **product-level UX, real-time data updates, and dashboard design principles**.

---
##  Live Demo
https://finsight-3ut5.onrender.com

## Setup
pip install -r requirements.txt  
python app.py


## Tech Stack

### Frontend

* HTML + CSS (custom styling)
* JavaScript (vanilla)
* Chart.js (data visualization)

### Backend

* Python (Flask)
* REST API endpoints

### Data

* JSON responses
* CSV upload support

---

## Architecture

```
Frontend (index.html)
        ↓
   Fetch API (REST)
        ↓
Backend (app.py)
        ↓
Insights Engine (insights.py)
        ↓
Database / Storage
```

---

##   Project Structure

```
/project
  ├── index.html        # Frontend UI
  ├── app.py            # Backend server
  ├── insights.py       # Insight logic
  └── database/storage
```

---

## Data Flow

* Client requests data via:

  * `/chart-data`
  * `/monthly-data`
  * `/insights`
  * `/get-stocks`

* Backend processes:

  * Transaction aggregation
  * Insight generation
  * Stock persistence

* Frontend dynamically updates:

  * Charts (Chart.js)
  * Insights (DOM rendering)
  * Watchlist (dynamic components)

---

## Key Concepts Used

### UI / UX

* CSS Grid (layout system)
* Flexbox (alignment)
* Card-based UI
* Dashboard ergonomics

### Data & Systems

* REST APIs
* JSON data handling
* Polling (simulated real-time)
* Client-server architecture

### Visualization

* Time-series analysis
* Category aggregation
* Interactive charts

---

## Tradeoffs & Decisions

| Decision                       | Reason                      |
| ------------------------------ | --------------------------- |
| Polling instead of WebSockets  | Simpler implementation      |
| Embedded stock charts (iframe) | Avoid building chart engine |
| Vanilla JS                     | No framework overhead       |
| Chart.js                       | Fast integration            |

---

---

##  Final Summary

FinSight is a **full-stack SaaS-style financial dashboard** that demonstrates:

* Real-world UI/UX design
* Data-driven insights
* API-based architecture
* Live updating systems

---

##  What Makes This Stand Out

* Not just CRUD — **actual product thinking**
* Focus on **usability and visibility**
* Includes **real-time-like behavior**
* Combines **finance + stocks + analytics**

---

## Author Notes

This project was built with a focus on:

* Practical engineering decisions
* Clean, readable UI
* Interview readiness

---
