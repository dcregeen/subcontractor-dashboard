import os
import gspread
import base64
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText

# ✅ Google API Scopes for Google Sheets & Gmail
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/gmail.send"
]

# ✅ Google API Credentials File (Ensure this file is in your project folder)
CREDS_FILE = "C:/Users/Dion/Python_Project/oauth_credentials.json"

# ✅ Google Sheets Information
SHEET_NAME = "Subcontractor Data Sheet"  # Update with your actual Google Sheet name
SHEET_RANGE = "A2:C"  # Adjust based on where emails & statuses are stored
LOG_FILE = "C:/Users/Dion/Python_Project/task_log.txt"  # Log file path

def authenticate_google_services():
    """Authenticate with Google APIs (Google Sheets & Gmail)."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # ✅ Save credentials for future use
        with open("token.json", "w") as token_file:
            token_file.write(creds.to_json())

    return creds

def get_unresponsive_subcontractors():
    """Fetch subcontractor emails from Google Sheets where status is 'Pending'."""
    creds = authenticate_google_services()
    gc = gspread.authorize(creds)
    sheet = gc.open(SHEET_NAME).sheet1
    records = sheet.get_all_values()

    subcontractors = []
    row_number = 2  # Google Sheets is 1-indexed, and row 1 is headers

    for row in records[1:]:  # Skip headers
        company_name = row[0]
        email = row[1]
        status = row[2]  # Adjust based on your Google Sheet structure

        if status.lower() == "pending":  # Only follow up with pending contacts
            subcontractors.append((row_number, company_name, email))

        row_number += 1  # Keep track of row number for updates

    return subcontractors

def send_email(service, recipient_email, recipient_name):
    """Send a follow-up email using Gmail API."""
    subject = f"Follow-Up: Subcontracting Partnership with {recipient_name}"
    message_text = f"""
    Dear {recipient_name} Team,

    We recently reached out regarding a potential subcontracting partnership with Cregeen GovWorks.
    We would love to discuss your capabilities further and explore contract opportunities together.

    Please let us know a convenient time for a quick call.

    Best regards,  
    Cregeen GovWorks Team
    """

    message = MIMEText(message_text)
    message["to"] = recipient_email
    message["subject"] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    try:
        service.users().messages().send(userId="me", body={"raw": raw_message}).execute()
        log_message(f"✅ Email sent to {recipient_email} ({recipient_name})")
        return True
    except Exception as e:
        log_message(f"❌ Error sending email to {recipient_email}: {e}")
        return False

def update_google_sheet(row_number):
    """Update Google Sheets status to 'Followed Up' after an email is sent."""
    creds = authenticate_google_services()
    gc = gspread.authorize(creds)
    sheet = gc.open(SHEET_NAME).sheet1
    sheet.update(f"C{row_number}", "Followed Up")  # Update Status column
    log_message(f"📌 Updated row {row_number}: Status → 'Followed Up'")

def log_message(message):
    """Log script execution time and status using UTF-8 encoding."""
    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(f"{datetime.datetime.now()} - {message}\n")
    print(message)


def main():
    """Main function to send follow-up emails and log them in Google Sheets."""
    creds = authenticate_google_services()
    gmail_service = build("gmail", "v1", credentials=creds)

    subcontractors = get_unresponsive_subcontractors()

    if not subcontractors:
        log_message("✅ No pending follow-ups!")
        return

    for row_number, name, email in subcontractors:
        if send_email(gmail_service, email, name):
            update_google_sheet(row_number)

if __name__ == "__main__":
    main()
