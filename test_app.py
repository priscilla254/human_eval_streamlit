import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("gspread_service_account.json", scope)
client = gspread.authorize(creds)

# Open the sheet
sheet = client.open("Human_Evaluation_Results").sheet1

# Append a test row
sheet.append_row([
    "test_user",
    "img001.png",
    "African",
    "20-29",
    4,
    5,
    4,
    datetime.now().isoformat()
])

print("✅ Test row successfully added!")
