from typing import Any, List, Optional

from googleapiclient.discovery import build
from google.oauth2 import service_account
from datetime import datetime
from pydantic import BaseModel, EmailStr
from enum import Enum

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = 'app/keys.json'

creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "1TUVioeOOqx5iP6iBMMuY-jv_BKS_GLMb6rVoBaWQDz0"

service = build("sheets", "v4", credentials=creds)
sheet = service.spreadsheets()

# Role-based access control
class Role(Enum):
    ROLE_ADMIN = "ADMIN"
    ROLE_VOLUNTEER = "VOLUNTEER"

def is_admin(email: Optional[str] = None, phone: Optional[str] = None) -> bool:
    """
    TODO: Check if the user ois a valid user using some auth mechanism
    :param email:
    :param phone:
    :return:
    """
    if email is None and phone is None:
        return False
    else:
        if email.lower() == "abc@abc.com":
            return True
        if phone.lower() == "12345":
            return True
    return True




# Call the Sheets API
"""
sheet = service.spreadsheets()
result = (
    sheet.values()
    .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="volunteers!A1:G16")
    .execute()
)
values = result.get("values", [])
print(values[1])




aoa = [["1/1/2020", 4000], ["4/4/2020", 5000],["6/6/2020", 6000]]
request = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID
                              ,range="volunteers!A1"
                              ,valueInputOption="USER_ENTERED"
                              ,body={"values":aoa})
response = request.execute()
print(response)
"""
print(Role.ROLE_ADMIN.value)