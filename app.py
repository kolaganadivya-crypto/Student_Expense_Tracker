import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from database import get_db_connection, init_db, get_settings, update_settings

# Supported Countries and their corresponding Currency and Symbol
COUNTRY_CURRENCY_MAP = {
    "India": {"currency": "INR", "currency_symbol": "₹"},
    "United States": {"currency": "USD", "currency_symbol": "$"},
    "United Kingdom": {"currency": "GBP", "currency_symbol": "£"},
    "European Union": {"currency": "EUR", "currency_symbol": "€"},
    "Japan": {"currency": "JPY", "currency_symbol": "¥"},
    "Canada": {"currency": "CAD", "currency_symbol": "C$"},
    "Australia": {"currency": "AUD", "currency_symbol": "A$"}
}

# Configure Flask app and point static files to the frontend folder
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")

# Enable Cross-Origin Resource Sharing (CORS) so API requests from any frontend port/origin work smoothly
CORS(app)

# Ensure database table exists when app starts
init_db()


# -------------------------------------------------------------
# Frontend Static Route
# -------------------------------------------------------------
@app.route("/")
def serve_frontend():
    """Serves the main HTML page of the application."""
    return send_from_directory(app.static_folder, "index.html")


# -------------------------------------------------------------
# REST API Endpoints
# -------------------------------------------------------------

@app.route("/api/expenses", methods=["GET"])
def get_expenses():
    """
    Fetch all expenses, with optional category filtering.
    Query parameter:
        category (optional): Filter expenses by exact category name.
    """
    category_filter = request.args.get("category")

    conn = get_db_connection()
    cursor = conn.cursor()

    if category_filter and category_filter.strip() != "" and category_filter.lower() != "all":
        cursor.execute(
            "SELECT * FROM expenses WHERE category = ? ORDER BY date DESC, id DESC",
            (category_filter.strip(),)
        )
    else:
        cursor.execute("SELECT * FROM expenses ORDER BY date DESC, id DESC")

    rows = cursor.fetchall()
    conn.close()

    # Convert SQLite Row objects to list of standard Python dictionaries
    expenses = [dict(row) for row in rows]
    return jsonify(expenses), 200


@app.route("/api/expenses/<int:expense_id>", methods=["GET"])
def get_expense(expense_id):
    """Fetch a single expense by its ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return jsonify({"error": "Expense not found"}), 404

    return jsonify(dict(row)), 200


@app.route("/api/expenses", methods=["POST"])
def add_expense():
    """
    Add a new expense.
    Expected JSON payload:
        {
            "amount": float / int,
            "category": string,
            "description": string,
            "date": "YYYY-MM-DD"
        }
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    amount = data.get("amount")
    category = data.get("category")
    description = data.get("description")
    date = data.get("date")

    # Validation: Ensure all fields are provided
    if amount is None or not category or not description or not date:
        return jsonify({"error": "All fields (amount, category, description, date) are required"}), 400

    # Validation: Amount must be a positive number
    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({"error": "Amount must be greater than zero"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Amount must be a valid number"}), 400

    # Insert into SQLite database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO expenses (amount, category, description, date) VALUES (?, ?, ?, ?)",
        (amount, category.strip(), description.strip(), date.strip())
    )
    conn.commit()
    new_id = cursor.lastrowid

    # Retrieve newly created expense
    cursor.execute("SELECT * FROM expenses WHERE id = ?", (new_id,))
    new_expense = dict(cursor.fetchone())
    conn.close()

    return jsonify({
        "message": "Expense added successfully",
        "expense": new_expense
    }), 201


@app.route("/api/expenses/<int:expense_id>", methods=["PUT"])
def update_expense(expense_id):
    """
    Update an existing expense by its ID.
    Expected JSON payload:
        {
            "amount": float / int,
            "category": string,
            "description": string,
            "date": "YYYY-MM-DD"
        }
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    amount = data.get("amount")
    category = data.get("category")
    description = data.get("description")
    date = data.get("date")

    if amount is None or not category or not description or not date:
        return jsonify({"error": "All fields (amount, category, description, date) are required"}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({"error": "Amount must be greater than zero"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Amount must be a valid number"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if expense exists
    cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
    if cursor.fetchone() is None:
        conn.close()
        return jsonify({"error": "Expense not found"}), 404

    # Update record
    cursor.execute(
        """
        UPDATE expenses
        SET amount = ?, category = ?, description = ?, date = ?
        WHERE id = ?
        """,
        (amount, category.strip(), description.strip(), date.strip(), expense_id)
    )
    conn.commit()

    # Retrieve updated record
    cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
    updated_expense = dict(cursor.fetchone())
    conn.close()

    return jsonify({
        "message": "Expense updated successfully",
        "expense": updated_expense
    }), 200


@app.route("/api/expenses/<int:expense_id>", methods=["DELETE"])
def delete_expense(expense_id):
    """Delete an expense by its ID."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
    if cursor.fetchone() is None:
        conn.close()
        return jsonify({"error": "Expense not found"}), 404

    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Expense deleted successfully"}), 200


@app.route("/api/settings", methods=["GET"])
def fetch_settings():
    """Returns the user's saved country, currency, and monthly budget settings."""
    settings = get_settings()
    return jsonify(settings), 200


@app.route("/api/settings", methods=["PUT"])
def save_settings():
    """
    Update country, currency, and monthly budget settings.
    Expected JSON payload:
        {
            "country": string (e.g. "India"),
            "monthly_budget": float (e.g. 10000.0)
        }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    country = data.get("country")
    if not country or country not in COUNTRY_CURRENCY_MAP:
        return jsonify({
            "error": f"Invalid country. Supported countries: {list(COUNTRY_CURRENCY_MAP.keys())}"
        }), 400

    budget = data.get("monthly_budget")
    if budget is None:
        return jsonify({"error": "monthly_budget is required"}), 400

    try:
        monthly_budget = float(budget)
        if monthly_budget < 0:
            return jsonify({"error": "Monthly budget cannot be negative"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "monthly_budget must be a valid number"}), 400

    currency = COUNTRY_CURRENCY_MAP[country]["currency"]
    currency_symbol = COUNTRY_CURRENCY_MAP[country]["currency_symbol"]

    updated = update_settings(country, currency, currency_symbol, monthly_budget)
    return jsonify({
        "message": "Settings saved successfully",
        "settings": updated
    }), 200


@app.route("/api/summary", methods=["GET"])
def get_summary():
    """
    Return high-level summary metrics:
    - Total expenses amount
    - Monthly budget
    - Remaining budget
    - Total transaction count
    - Breakdown by category
    - Active currency settings
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Calculate overall total and count
    cursor.execute("SELECT COUNT(*) AS total_count, COALESCE(SUM(amount), 0) AS total_amount FROM expenses")
    overview = dict(cursor.fetchone())

    # Calculate breakdown grouped by category
    cursor.execute(
        """
        SELECT category, COALESCE(SUM(amount), 0) AS category_total, COUNT(*) AS count
        FROM expenses
        GROUP BY category
        ORDER BY category_total DESC
        """
    )
    categories = [dict(row) for row in cursor.fetchall()]
    conn.close()

    settings = get_settings()
    total_spent = round(overview["total_amount"], 2)
    monthly_budget = round(float(settings["monthly_budget"]), 2)
    remaining_budget = round(monthly_budget - total_spent, 2)

    return jsonify({
        "total_amount": total_spent,
        "total_count": overview["total_count"],
        "monthly_budget": monthly_budget,
        "remaining_budget": remaining_budget,
        "country": settings["country"],
        "currency": settings["currency"],
        "currency_symbol": settings["currency_symbol"],
        "category_breakdown": categories
    }), 200


# -------------------------------------------------------------
# Run the Development Server
# -------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Flask server on http://0.0.0.0:{port} ...")
    app.run(host="0.0.0.0", port=port, debug=False)
