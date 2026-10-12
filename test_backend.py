import sys
import os
import unittest
import json

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app import app
from database import get_db_connection, init_db

class TestExpenseTracker(unittest.TestCase):
    def setUp(self):
        # Set Flask app to testing mode
        app.config["TESTING"] = True
        self.client = app.test_client()

        # Clean table before each test
        conn = get_db_connection()
        conn.execute("DELETE FROM expenses")
        conn.commit()
        conn.close()

    def test_01_create_expense(self):
        payload = {
            "amount": 14.50,
            "category": "Food & Dining",
            "description": "Campus Cafeteria Lunch",
            "date": "2026-10-03"
        }
        res = self.client.post("/api/expenses", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertIn("expense", data)
        self.assertEqual(data["expense"]["amount"], 14.50)
        self.assertEqual(data["expense"]["category"], "Food & Dining")

    def test_02_validation_invalid_amount(self):
        payload = {
            "amount": -5.00,
            "category": "Books & Supplies",
            "description": "Notebook",
            "date": "2026-10-03"
        }
        res = self.client.post("/api/expenses", json=payload)
        self.assertEqual(res.status_code, 400)

    def test_03_get_expenses_and_summary(self):
        # Add 2 sample expenses
        self.client.post("/api/expenses", json={
            "amount": 25.00,
            "category": "Books & Supplies",
            "description": "Math Textbook",
            "date": "2026-10-01"
        })
        self.client.post("/api/expenses", json={
            "amount": 10.00,
            "category": "Food & Dining",
            "description": "Coffee and Snack",
            "date": "2026-10-02"
        })

        # Test GET all
        res = self.client.get("/api/expenses")
        self.assertEqual(res.status_code, 200)
        expenses = res.get_json()
        self.assertEqual(len(expenses), 2)

        # Test GET with filter
        filtered_res = self.client.get("/api/expenses?category=Books %26 Supplies")
        self.assertEqual(filtered_res.status_code, 200)
        filtered_expenses = filtered_res.get_json()
        self.assertEqual(len(filtered_expenses), 1)
        self.assertEqual(filtered_expenses[0]["category"], "Books & Supplies")

        # Test GET summary
        sum_res = self.client.get("/api/summary")
        self.assertEqual(sum_res.status_code, 200)
        summary = sum_res.get_json()
        self.assertEqual(summary["total_count"], 2)
        self.assertEqual(summary["total_amount"], 35.00)

    def test_04_update_expense(self):
        # Create an expense
        create_res = self.client.post("/api/expenses", json={
            "amount": 20.00,
            "category": "Transportation",
            "description": "Bus pass",
            "date": "2026-10-01"
        })
        expense_id = create_res.get_json()["expense"]["id"]

        # Update it
        update_payload = {
            "amount": 22.50,
            "category": "Transportation",
            "description": "Monthly Metro Pass",
            "date": "2026-10-01"
        }
        put_res = self.client.put(f"/api/expenses/{expense_id}", json=update_payload)
        self.assertEqual(put_res.status_code, 200)
        updated = put_res.get_json()["expense"]
        self.assertEqual(updated["amount"], 22.50)
        self.assertEqual(updated["description"], "Monthly Metro Pass")

    def test_05_delete_expense(self):
        # Create an expense
        create_res = self.client.post("/api/expenses", json={
            "amount": 5.00,
            "category": "Other",
            "description": "Pen",
            "date": "2026-10-02"
        })
        expense_id = create_res.get_json()["expense"]["id"]

        # Delete it
        del_res = self.client.delete(f"/api/expenses/{expense_id}")
        self.assertEqual(del_res.status_code, 200)

        # Confirm it's gone
        get_res = self.client.get(f"/api/expenses/{expense_id}")
        self.assertEqual(get_res.status_code, 404)

    def test_06_default_settings(self):
        # Reset to default
        self.client.put("/api/settings", json={"country": "India", "monthly_budget": 10000.0})
        res = self.client.get("/api/settings")
        self.assertEqual(res.status_code, 200)
        settings = res.get_json()
        self.assertEqual(settings["country"], "India")
        self.assertEqual(settings["currency"], "INR")
        self.assertEqual(settings["currency_symbol"], "₹")
        self.assertEqual(settings["monthly_budget"], 10000.0)

    def test_07_update_and_persist_settings(self):
        payload = {
            "country": "United States",
            "monthly_budget": 2500.0
        }
        put_res = self.client.put("/api/settings", json=payload)
        self.assertEqual(put_res.status_code, 200)
        data = put_res.get_json()["settings"]
        self.assertEqual(data["country"], "United States")
        self.assertEqual(data["currency"], "USD")
        self.assertEqual(data["currency_symbol"], "$")
        self.assertEqual(data["monthly_budget"], 2500.0)

        # Confirm persistence with GET
        get_res = self.client.get("/api/settings")
        self.assertEqual(get_res.status_code, 200)
        persisted = get_res.get_json()
        self.assertEqual(persisted["currency"], "USD")
        self.assertEqual(persisted["monthly_budget"], 2500.0)

    def test_08_settings_validation(self):
        # Invalid country
        res1 = self.client.put("/api/settings", json={"country": "Mars", "monthly_budget": 1000})
        self.assertEqual(res1.status_code, 400)

        # Negative budget
        res2 = self.client.put("/api/settings", json={"country": "India", "monthly_budget": -50})
        self.assertEqual(res2.status_code, 400)

    def test_09_summary_budget_calculation(self):
        # Set budget to 10,000 for India
        self.client.put("/api/settings", json={"country": "India", "monthly_budget": 10000.0})

        # Add 6,250 expense (matching user's example: Monthly 10000, Spent 6250, Remaining 3750)
        self.client.post("/api/expenses", json={
            "amount": 6250.00,
            "category": "Food & Dining",
            "description": "Monthly Mess & Groceries",
            "date": "2026-10-01"
        })

        sum_res = self.client.get("/api/summary")
        self.assertEqual(sum_res.status_code, 200)
        summary = sum_res.get_json()
        self.assertEqual(summary["total_amount"], 6250.0)
        self.assertEqual(summary["monthly_budget"], 10000.0)
        self.assertEqual(summary["remaining_budget"], 3750.0)
        self.assertEqual(summary["currency_symbol"], "₹")
        self.assertEqual(summary["currency"], "INR")

    def test_10_summary_budget_exceeded(self):
        # When expenses exceed monthly budget
        self.client.put("/api/settings", json={"country": "India", "monthly_budget": 5000.0})
        self.client.post("/api/expenses", json={
            "amount": 5500.00,
            "category": "Rent & Housing",
            "description": "Campus Hostel Room",
            "date": "2026-10-01"
        })

        sum_res = self.client.get("/api/summary")
        self.assertEqual(sum_res.status_code, 200)
        summary = sum_res.get_json()
        self.assertEqual(summary["total_amount"], 5500.0)
        self.assertEqual(summary["monthly_budget"], 5000.0)
        self.assertEqual(summary["remaining_budget"], -500.0)

if __name__ == "__main__":
    unittest.main()
