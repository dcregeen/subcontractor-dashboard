import sqlite3
import pandas as pd

# ✅ Database Name
DB_NAME = "subcontractors.db"

def create_database():
    """Creates a subcontractor tracking database if it doesn’t exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS subcontractors (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        company_name TEXT,
                        naics_code TEXT,
                        uei_code TEXT,
                        cage_code TEXT,
                        poc_name TEXT,
                        email TEXT,
                        phone TEXT,
                        contract_history TEXT,
                        status TEXT)''')

    conn.commit()
    conn.close()
    print("✅ Subcontractor database created!")

def add_subcontractor(company_name, naics_code, uei_code, cage_code, poc_name, email, phone, contract_history, status):
    """Adds a new subcontractor to the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("INSERT INTO subcontractors (company_name, naics_code, uei_code, cage_code, poc_name, email, phone, contract_history, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   (company_name, naics_code, uei_code, cage_code, poc_name, email, phone, contract_history, status))

    conn.commit()
    conn.close()
    print(f"✅ {company_name} added to the database!")

def get_all_subcontractors():
    """Fetches all subcontractors and displays them in a table."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT * FROM subcontractors", conn)
    conn.close()

    if df.empty:
        print("📌 No subcontractors found in the database.")
    else:
        print("📋 Subcontractor Database:")
        print(df.to_string(index=False))  # Display data in a readable format

def update_subcontractor_status(subcontractor_id, new_status):
    """Updates the status of a subcontractor."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("UPDATE subcontractors SET status = ? WHERE id = ?", (new_status, subcontractor_id))

    conn.commit()
    conn.close()
    print(f"✅ Subcontractor ID {subcontractor_id} status updated to {new_status}!")

def delete_subcontractor(subcontractor_id):
    """Deletes a subcontractor from the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM subcontractors WHERE id = ?", (subcontractor_id,))

    conn.commit()
    conn.close()
    print(f"✅ Subcontractor ID {subcontractor_id} deleted!")

# ✅ Run this once to create the database
create_database()

# ✅ Example: Adding a new subcontractor
add_subcontractor("ABC Logistics", "541614", "M12345", "0QXYZ", "John Doe", "john@abclogistics.com", "555-1234", "Past Performance: DoD Contract 2023", "Pending")

# ✅ Fetch and display subcontractor data
get_all_subcontractors()
