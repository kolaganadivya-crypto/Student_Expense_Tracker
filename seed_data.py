"""
Helper script to populate realistic student expenses for testing.
Run with: python seed_data.py [--reset]
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
from database import get_db_connection, init_db, update_settings

SAMPLE_EXPENSES = [
    (1250.00, "Books & Supplies", "Calculus and Engineering Mechanics Textbooks", "2026-10-01"),
    (500.00, "Food & Dining", "Campus Cafeteria Meal Coupons", "2026-10-02"),
    (180.00, "Food & Dining", "Evening Tea & Snacks with Study Group", "2026-10-02"),
    (750.00, "Transportation", "Monthly Metro & Bus Pass Recharge", "2026-09-28"),
    (650.00, "Entertainment", "Weekend Movie & Popcorn with Friends", "2026-09-30"),
    (380.00, "Personal Care", "Stationery & Notebooks", "2026-10-03")
]

def seed(reset=False):
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    if reset:
        cursor.execute("DELETE FROM expenses")
        conn.commit()

    cursor.execute("SELECT COUNT(*) FROM expenses")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.executemany(
            "INSERT INTO expenses (amount, category, description, date) VALUES (?, ?, ?, ?)",
            SAMPLE_EXPENSES
        )
        conn.commit()
        print(f"Added {len(SAMPLE_EXPENSES)} student expenses to the database.")
    else:
        print(f"Database already contains {count} records. No new seed data added.")

    conn.close()
    # Reset settings to default India / INR / 10000.0
    update_settings("India", "INR", "₹", 10000.0)

if __name__ == "__main__":
    reset_flag = "--reset" in sys.argv
    seed(reset=reset_flag)
