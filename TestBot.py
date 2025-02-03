import requests
import sqlite3
import smtplib
import datetime
from email.message import EmailMessage
import pandas as pd

# SAM.gov API Key (Replace with yours)
SAM_API_KEY = "MDGUz7pSdDBOUZy3Ph3XEadqRrzlFmHhe0ZRWzbD"

# ClickUp API Key (Optional, for integration)
CLICKUP_API_KEY = "pk_120238544_9OCK6A96YSS5RCDN3VZP92LAWE9D9FS2"

# NAICS Codes & Keywords for filtering
NAICS_CODES = ["541512", "561210"]  # Example: IT Services, Facilities Support
KEYWORDS = ["cybersecurity", "IT support", "logistics"]

# Email Configuration
EMAIL_SENDER = "your_email@example.com"
EMAIL_RECEIVER = "your_email@example.com"
EMAIL_PASSWORD = "your_password"

# SQLite Database setup
DB_NAME = "sam_opportunities.db"

def create_database():
    """Creates an SQLite database to store SAM.gov opportunities."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS opportunities (
                        id TEXT PRIMARY KEY,
                        title TEXT,
                        naics TEXT,
                        agency TEXT,
                        due_date TEXT,
                        url TEXT)''')
    conn.commit()
    conn.close()

def fetch_sam_opportunities():
    """Fetches opportunities from SAM.gov API with a date range."""
    
    # Get today's date and 7 days ago (format: YYYY-MM-DD)
    today = datetime.date.today().strftime("%Y-%m-%d")
    seven_days_ago = (datetime.date.today() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")

    url = f"https://api.sam.gov/prod/opportunities/v2/search?api_key={SAM_API_KEY}"

    params = {
        "limit": 10,  # Adjust the number of results
        "sort": "publishDate",
        "order": "desc",
        "postedFrom": seven_days_ago,
        "postedTo": today
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching SAM.gov data:", response.text)
        return None

def filter_opportunities(data):
    """Filters opportunities based on NAICS codes and keywords."""
    filtered = []
    
    for item in data.get("opportunitiesData", []):
        naics = item.get("naicsCode", "")
        title = item.get("title", "").lower()
        if naics in NAICS_CODES or any(kw in title for kw in KEYWORDS):
            filtered.append({
                "id": item["id"],
                "title": item["title"],
                "naics": naics,
                "agency": item.get("departmentName", "N/A"),
                "due_date": item.get("responseDeadline", "N/A"),
                "url": item.get("noticeUrl", "")
            })
    
