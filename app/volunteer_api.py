from enum import Enum
from fastapi import HTTPException

from fastapi import FastAPI, APIRouter
from google.oauth2 import service_account
from pydantic import BaseModel
import gspread
import re

# Create a new router for volunteer
volunteer_router = APIRouter()

class Volunteer(BaseModel):
    full_name: str
    email: str
    mobile: str
    location: str
    gender: str
    preferred_days_to_volunteer: str
    is_active: bool=None

class STATUS(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    NEW = "NEW"

app = FastAPI()

# Set up the Google Sheets API client
def authenticate_google_sheets():
    # Define the scope for Google Sheets API
    scope = ["https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
              ]
    service_account_file = 'app/keys.json'

    # Authenticate with the service account credentials file
    creds = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=scope)

    # Use the credentials to authorize the client
    client = gspread.authorize(creds)
    return client

def is_existing_volunteer(client: gspread.Client, email: str) -> bool:
    """
    Finds a volunteer by email.
    :param client:
    :param email:
    :return:
    """
    print(f"Email given: {email}")
    spreadsheet = client.open("SSDVolunteers").sheet1
    volunteers = spreadsheet.get_all_records()
    for volunteer in volunteers:
        print(f"current volunteer: {volunteer}")
        if volunteer["Email"] == email:
            return True
    return False

# Helper function to add a new volunteer to the sheet

@volunteer_router.post("/volunteers/add",
          responses={409: {"description": "Volunteer already exists"}, 201: {"description": "Volunteer added successfully"}},
          summary="Add new volunteer",
          response_model=Volunteer)
async def add_volunteer_to_sheet(volunteer: Volunteer):

    if len(volunteer.mobile) == 11:
        volunteer.mobile = volunteer.mobile[1:] # Slice to remove the first character
    elif len(volunteer.mobile) > 11:
        raise HTTPException(status_code=400, detail="Please provide a valid phone number")

    volunteer_data = [volunteer.full_name,
                      volunteer.email,
                      re.sub(r'[^0-9]', '', volunteer.mobile),
                      volunteer.location,
                      volunteer.gender,
                      volunteer.preferred_days_to_volunteer,
                      STATUS.NEW.value]

    print(f"volunteer_data: {volunteer_data}")

    # append volunteer to the sheet
    request_client = authenticate_google_sheets()
    spreadsheet = request_client.open("SSDVolunteers").sheet1



    if is_existing_volunteer(request_client, volunteer_data[1]):
        raise HTTPException(status_code=409, detail="Volunteer exists")
    spreadsheet.append_row(volunteer_data)
    return volunteer

