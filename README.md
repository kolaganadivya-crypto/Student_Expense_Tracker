# 🎓 Student Expense Tracker (Full-Stack Web App)

A clean, modern, beginner-friendly full-stack web application designed for college students to track daily spending, monitor budgets, and organize campus finances.

---

## 🛠️ Technology Stack

- **Frontend**: HTML5, CSS3, Vanilla JavaScript (ES6+ `fetch()` API)
- **Backend**: Python 3, Flask, Flask-CORS
- **Database**: SQLite3
- **Communication Protocol**: RESTful API with JSON payloads

---

## 🌟 Upgraded Features

1. **Country & Currency Personalization**:
   - Choose from 7 countries with native currency symbols and formatting:
     - 🇮🇳 India $\rightarrow$ INR (₹) *(Default)*
     - 🇺🇸 United States $\rightarrow$ USD ($)
     - 🇬🇧 United Kingdom $\rightarrow$ GBP (£)
     - 🇪🇺 European Union $\rightarrow$ EUR (€)
     - 🇯🇵 Japan $\rightarrow$ JPY (¥)
     - 🇨🇦 Canada $\rightarrow$ CAD (C$)
     - 🇦🇺 Australia $\rightarrow$ AUD (A$)
   - Formats monetary values with correct symbol and locale (e.g. `₹500.00`, `₹1,250.00`).
   - Dynamic form prefix and labels that adjust when currency changes.
2. **Persistent Preferences**:
   - Selected country, currency, and monthly budget are saved directly into the SQLite database (`settings` table).
   - Preferences remain preserved even after browser reloads.
3. **Monthly Budget Tracking**:
   - Set and adjust your monthly spending budget.
   - Live dashboard cards displaying:
     - **Total Spent**
     - **Monthly Budget**
     - **Remaining Budget** (highlights green when on budget, warning red with ⚠️ alert if exceeded)
     - **Total Expenses Count**
     - **Top Spending Category**
4. **Intuitive Settings Modal**:
   - Easily accessible `⚙️ Settings` button in the navigation header with live country/currency badge preview.
5. **Existing Features Preserved**:
   - Full Add, Edit, Delete (with confirmation modal), Category Filtering, and summary metrics.

---

## 📁 Project Structure

```text
Student_Expense_Tracker/
│
├── backend/
│   ├── app.py             # Flask REST API server, settings & static file host
│   ├── database.py        # SQLite connection, expenses & settings table schema
│   └── expenses.db        # SQLite database file (auto-generated)
│
├── frontend/
│   ├── index.html         # User interface layout, 5-card dashboard & settings modal
│   ├── style.css          # Responsive design, custom student theme & modal styles
│   └── app.js             # Vanilla JS for API communication, budget math & DOM updates
│
├── requirements.txt       # Python package dependencies (Flask, Flask-CORS)
├── seed_data.py           # Helper script to populate sample student expenses
├── test_backend.py        # Comprehensive test suite (10 unit tests)
└── README.md              # Project documentation & run guide
```

---

## 🚀 How to Run the Application

### 1. Install Dependencies
Open your terminal in the project directory and run:
```bash
pip install -r requirements.txt
```

### 2. (Optional) Seed Sample Data
To populate realistic student expenses and reset to default Indian Rupee settings:
```bash
python seed_data.py --reset
```

### 3. Start the Flask Backend Server
```bash
python backend/app.py
```

### 4. Open in Your Browser
Visit:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 📡 REST API Reference

| Method | Endpoint | Description | Request Body | Response |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/expenses` | Fetch all expenses (or filter via `?category=...`) | None | Array of expense objects |
| `GET` | `/api/expenses/<id>` | Fetch a single expense by ID | None | Expense object or 404 |
| `POST` | `/api/expenses` | Add a new expense | JSON with `amount`, `category`, `description`, `date` | `201 Created` + new object |
| `PUT` | `/api/expenses/<id>` | Update an existing expense | JSON with updated fields | `200 OK` + updated object |
| `DELETE` | `/api/expenses/<id>` | Delete an expense by ID | None | `200 OK` + success message |
| `GET` | `/api/summary` | Get spent, budget, remaining, count, top category | None | Summary statistics object |
| `GET` | `/api/settings` | Get user country, currency, symbol, and budget | None | Settings object |
| `PUT` | `/api/settings` | Update country and monthly budget | JSON with `country`, `monthly_budget` | `200 OK` + updated settings |

---

## 🧪 Running the Automated Tests

To run the complete test suite verifying all 10 unit tests:
```bash
python test_backend.py
```
Expected output:
```text
Ran 10 tests in 0.3s
OK
```
