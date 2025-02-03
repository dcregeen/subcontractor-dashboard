from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import pandas as pd

# ✅ Initialize Flask App
app = Flask(__name__)

# ✅ Database Name
DB_NAME = "subcontractors.db"

def get_db_connection():
    """Connect to SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# ✅ Home Route: View All Subcontractors
@app.route('/')
def index():
    conn = get_db_connection()
    subcontractors = conn.execute('SELECT * FROM subcontractors').fetchall()
    conn.close()
    return render_template('index.html', subcontractors=subcontractors)

# ✅ Add Subcontractor Route (Prevent Duplicates)
@app.route('/add', methods=['POST'])
def add_subcontractor():
    company_name = request.form['company_name']
    naics_code = request.form['naics_code']
    uei_code = request.form['uei_code']
    cage_code = request.form['cage_code']
    poc_name = request.form['poc_name']
    email = request.form['email']
    phone = request.form['phone']
    contract_history = request.form['contract_history']
    status = request.form['status']

    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ Check if the subcontractor already exists (by Company Name + UEI Code)
    cursor.execute("SELECT * FROM subcontractors WHERE company_name = ? AND uei_code = ?", (company_name, uei_code))
    existing = cursor.fetchone()

    if existing:
        print("⚠️ Subcontractor already exists. Skipping duplicate entry.")
    else:
        cursor.execute("INSERT INTO subcontractors (company_name, naics_code, uei_code, cage_code, poc_name, email, phone, contract_history, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (company_name, naics_code, uei_code, cage_code, poc_name, email, phone, contract_history, status))
        conn.commit()
        print(f"✅ Added new subcontractor: {company_name}")

    conn.close()
    return redirect(url_for('index'))


# ✅ Delete Subcontractor Route
@app.route('/delete/<int:subcontractor_id>')
def delete_subcontractor(subcontractor_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM subcontractors WHERE id = ?", (subcontractor_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# ✅ Update Subcontractor Route
@app.route('/update/<int:subcontractor_id>', methods=['POST'])
def update_subcontractor(subcontractor_id):
    status = request.form['status']
    conn = get_db_connection()
    conn.execute("UPDATE subcontractors SET status = ? WHERE id = ?", (status, subcontractor_id))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# ✅ Run Flask App
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)

