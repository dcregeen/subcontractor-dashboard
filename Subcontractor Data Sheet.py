import gspread
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# ✅ OAuth 2.0 Credentials File (Make sure this path is correct)
CREDS_FILE = "C:/Users/Dion/Python_Project/oauth_credentials.json"

# ✅ Correct API Scopes for Google Sheets & Drive Access
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

def authenticate_google_sheets():
    """Authenticates with Google Sheets API using OAuth 2.0."""
    creds = None

    # ✅ Check if token.json exists (previous authentication)
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # ✅ If no valid credentials, authenticate via OAuth
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # ✅ Save credentials for future use
        with open("token.json", "w") as token_file:
            token_file.write(creds.to_json())

    return gspread.authorize(creds)

# ✅ Delete old token.json (if scopes changed)
if os.path.exists("token.json"):
    os.remove("token.json")

# ✅ Authenticate and connect to Google Sheets
gc = authenticate_google_sheets()

# ✅ Open Google Sheets Document (Update with your actual Google Sheet name)
SPREADSHEET_NAME = "Subcontractor Data Sheet"
spreadsheet = gc.open(SPREADSHEET_NAME)
worksheet = spreadsheet.sheet1  # First sheet

print("✅ Successfully connected to Google Sheets!")
