import sqlite3
import gspread
import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# ✅ Google Sheets Details
GOOGLE_SHEETS_URL = "YOUR_GOOGLE_SHEET_URL"  # 🔴 Replace with your actual Google Sheets URL
CREDS_FILE = "C:/Users/Dion/Python_Project/oauth_client.json"
TOKEN_FILE = "C:/Users/Dion/Python_Project/token.json"

# ✅ Authenticate Using OAuth 2.0
def authenticate_google():
    creds = None

    # ✅ Check if token.json exists (previous authentication)
    try:
        creds = Credentials.from_authorized_user_file(TOKEN_FILE)
    except:
        pass

    # ✅ If no valid credentials, authenticate via OAuth
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, ["https://www.googleapis.com/auth/spreadsheets"])
        creds = flow.run_local_server(port=0)

        # ✅ Save credentials for future use
        with open(TOKEN_FILE, "w") as token_file:
            token_file.write(creds.to_json())

    return gspread.authorize(creds)

# ✅ Connect to Google Sheets
def connect_to_sheets():
    client = authenticate_google()
    return client.open_by_url(GOOGLE_SHEETS_URL).sheet1  # Use first sheet

# ✅ Connect to SQLite Database
DB_NAME = "subcontractors.db"

def connect_to_db():
    return sqlite3.connect(DB_NAME)

# ✅ Export Database to Google Sheets
def export_to_sheets():
    conn = connect_to_db()
    df = pd.read_sql("SELECT * FROM subcontractors", conn)
    conn.close()

    sheet = connect_to_sheets()
    sheet.clear()  # Clear existing data

    # ✅ Add Headers to Google Sheets
    headers = ["ID", "Company Name", "NAICS Code", "UEI Code", "CAGE Code", "POC Name", "Email", "Phone", "Contract History", "Status"]
    sheet.append_row(headers)

    # ✅ Convert DataFrame to List of Lists (Each row as a separate list)
    data = df.values.tolist()

    if data:  # Only append if data exists
        sheet.append_rows(data, value_input_option="RAW")

    print("✅ Database successfully exported to Google Sheets!")

# ✅ Import Google Sheets Data into SQLite
def import_from_sheets():
    conn = connect_to_db()
    cursor = conn.cursor()
    sheet = connect_to_sheets()

    # ✅ Fetch Data from Google Sheets
    records = sheet.get_all_values()[1:]  # Skip header row

    if records:  # Only insert if there's data
        cursor.execute("DELETE FROM subcontractors")  # Clear table before importing
        cursor.executemany("INSERT INTO subcontractors VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", records)

    conn.commit()
    conn.close()
    print("✅ Google Sheets successfully imported into database!")

# ✅ Run Both Sync Functions
export_to_sheets()  # Send database to Google Sheets
import_from_sheets()  # Get Google Sheets data into the database
