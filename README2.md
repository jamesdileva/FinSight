# 💰 FinSight

FinSight is a personal finance dashboard that helps you track spending, visualize trends, and monitor stocks — all in one place.

---

## 🚀 Features

* 📊 Category breakdown (pie chart)
* 📈 Monthly spending trends (line chart)
* 🧠 Smart insights (auto-generated)
* 📂 CSV upload for bulk transactions
* ➕ Manual transaction entry
* 📉 Stock tracker + watchlist
* 🔐 User authentication (login/register)

---

## 🛠️ Tech Stack

* Backend: Flask
* Database: SQLite
* Frontend: HTML, CSS, JavaScript
* Charts: Chart.js

---

## ⚙️ Setup (Local Development)

### 1. Clone the repo

```bash
git clone https://github.com/your-username/finsight.git
cd finsight
```

### 2. Create virtual environment (recommended)

```bash
python -m venv venv
venv\Scripts\activate   # Windows
# or
source venv/bin/activate  # Mac/Linux
```

### 3. Install dependencies

```bash
pip install flask python-dotenv werkzeug
```

### 4. Run the app

```bash
python app.py
```

### 5. Open in browser

```
http://127.0.0.1:5000
```

---

## 📂 CSV Upload Format

Your CSV file must include:

```csv
amount,category,date,description
50,Food,2026-03-01,Lunch
1200,Rent,2026-03-01,Apartment
```

---

## 🔐 Environment Variables (Optional)

Create a `.env` file:

```
SECRET_KEY=your_secret_key_here
```

---

## 🌐 Deployment

This app is designed to be deployed using platforms like Render.

---

## ⚠️ Notes

* SQLite is used for local development
* Data may reset on some hosting platforms
* Future upgrade: PostgreSQL support

---

## 📌 Future Improvements

* Budget tracking
* Recurring expenses
* Better stock analytics
* Mobile responsiveness

---

## 👨‍💻 Author

Built by James 🚀
