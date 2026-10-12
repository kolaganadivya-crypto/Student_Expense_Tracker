import sqlite3
import os

# Path to the SQLite database file
DB_NAME = "expenses.db"
DB_PATH = os.path.join(os.path.dirname(__file__), DB_NAME)

def get_db_connection():
    """
    Establishes and returns a connection to the SQLite database.
    Setting row_factory to sqlite3.Row allows us to access columns by name
    (like Python dictionaries), making it easy to convert rows to JSON.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initializes the database by creating 'expenses' and 'settings' tables if they do not exist.
    Inserts default settings (Country: India, Currency: INR, Symbol: ₹, Budget: 10000.0).
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            country TEXT NOT NULL DEFAULT 'India',
            currency TEXT NOT NULL DEFAULT 'INR',
            currency_symbol TEXT NOT NULL DEFAULT '₹',
            monthly_budget REAL NOT NULL DEFAULT 10000.0
        )
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO settings (id, country, currency, currency_symbol, monthly_budget)
        VALUES (1, 'India', 'INR', '₹', 10000.0)
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

def get_settings():
    """Fetches the application settings."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT country, currency, currency_symbol, monthly_budget FROM settings WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return {
        "country": "India",
        "currency": "INR",
        "currency_symbol": "₹",
        "monthly_budget": 10000.0
    }

def update_settings(country, currency, currency_symbol, monthly_budget):
    """Updates the application settings in SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE settings
        SET country = ?, currency = ?, currency_symbol = ?, monthly_budget = ?
        WHERE id = 1
    """, (country, currency, currency_symbol, monthly_budget))
    conn.commit()
    cursor.execute("SELECT country, currency, currency_symbol, monthly_budget FROM settings WHERE id = 1")
    updated = dict(cursor.fetchone())
    conn.close()
    return updated

if __name__ == "__main__":
    init_db()
