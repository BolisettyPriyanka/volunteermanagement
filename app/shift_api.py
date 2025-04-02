from typing import List, Optional

from fastapi import HTTPException

from fastapi import FastAPI, APIRouter
from google.oauth2 import service_account
from pydantic import BaseModel
import gspread


# Create a new router for volunteer
shift_router = APIRouter()

class Shift(BaseModel):
    shift_name: str
    start_time: str
    end_time: str
    volunteers: str
    responsibilities: str
    is_available: str


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

def is_valid_phone(client: gspread.Client, phone: str) -> bool:
    """
    Finds if a phone number is valid.
    :param client:
    :param phone:
    :return:
    """
    spreadsheet = client.open("SSDVolunteers").sheet1
    volunteers = spreadsheet.get_all_records()
    for volunteer in volunteers:
        if phone == volunteer['Mobile']:
            print(f"volunteer: {volunteer}")
            print(f"found phone match: {phone}")
            return True
    return False

def is_existing_shift(client: gspread.Client, name: str, start_time: str) -> bool:
    """
    Finds a shift by name and its start_time.
    :param client:
    :param name:
    :param start_time:
    :return:
    """
    print(f"Name given: {name}")
    spreadsheet = client.open("SSDVolunteers")

    # Access the second sheet (using index 1 since index is 0-based)
    shift_sheet = spreadsheet.worksheet("shifts")

    shifts = shift_sheet.get_all_records()
    print(f"Found {len(shifts)} shifts")
    print(shifts)
    for shift in shifts:
        print(f"current volunteer: {shift}")
        if shift["Shift Name"] == name and shift["Start Time"] == start_time:
            return True
    return False

def get_all_shifts(client: gspread.Client) -> list[dict[str, int | float | str]]:
    """
    Helper function to get all shifts by name.
    :param client:
    :param name:
    :return:
    """

    spreadsheet = client.open("SSDVolunteers")

    # Access the second sheet (using index 1 since index is 0-based)
    shift_sheet = spreadsheet.worksheet("shifts")
    return shift_sheet.get_all_records()


# Helper function to lookup shifts by phone number
def get_shifts(client: gspread.Client, phone_number: Optional[str] = None) -> list[dict[str, int | float | str]]:
    print(f"phone given: {phone_number}")
    shifts = get_all_shifts(client)

    print(f"Found {len(shifts)} shifts")
    shifts_list = []
    for shift in shifts:
        phone_numbers = shift["Volunteers"].split(", ")
        for phone in phone_numbers:
            if phone == phone_number:
                print(f"shift match found: {shift}")
                shifts_list.append(shift)
    print(f"Found matching shifts: {shifts_list}    ")
    return shifts_list


@shift_router.post("/shifts/add",
          responses={409: {"description": "Shift already exists"}, 201: {"description": "Shift added successfully"}},
          summary="Add new volunteer",
          response_model=Shift)
async def add_shift_to_sheet(shift: Shift):

    shift_data = [shift.shift_name,
                      shift.start_time,
                      shift.end_time,
                      shift.volunteers,
                      shift.responsibilities]

    print(f"shift_data: {shift_data}")

    # append shift to the sheet
    request_client = authenticate_google_sheets()
    spreadsheet = request_client.open("SSDVolunteers")

    if is_existing_shift(request_client, shift_data[0], shift_data[1]):
        raise HTTPException(status_code=409, detail="Shift exists")
    spreadsheet.worksheet("shifts").append_row(shift_data)
    return shift


def get_shifts_by_phone_number(phone: str):
    print(f"phone_number: {phone}")

    # Authenticate the sheet
    request_client = authenticate_google_sheets()

    if phone is None:
        raise HTTPException(status_code=400, detail="Bad request")

    return get_shifts(request_client, phone)


def get_available_shifts(phone: str):
    print(f"phone: {phone}")

    # Authenticate the sheet
    request_client = authenticate_google_sheets()

    if not is_valid_phone(request_client, phone):
        raise HTTPException(status_code=400, detail="phone number is invalid")

    shifts = get_all_shifts(request_client)
    available_shifts = []

    for shift in shifts:
        if phone not in shift["Volunteers"] and shift["Is Available"] == "Yes":
            print(f"shift: {shift}")
            available_shifts.append(shift)
    return available_shifts

# Function to delete a phone number from a specific row
def delete_phone_number_from_row(sheet, shift_column, phone_number):
    # Get all rows from the sheet
    rows = sheet.get_all_values()

    # Iterate through rows to find the shift containing the phone number
    for i, row in enumerate(rows):
        # Assume the shift info is in the first column and phone numbers in the specified shift column
        shift_column_data = row[3]
        print(f"shift_column_data : {shift_column_data}")

        # Split the phone numbers by a delimiter (assuming they are comma-separated)
        shift_column_data.replace(" ", "")
        phone_numbers = shift_column_data.split(',')

        if phone_number in phone_numbers:
            # Remove the phone number
            phone_numbers.remove(phone_number)

            # Update the row with the new list of phone numbers
            sheet.update_cell(i + 1, shift_column + 1, ','.join(phone_numbers))  # +1 because gspread is 1-indexed
            print(f"Removed {phone_number} from shift {i + 1}.")
            break
    else:
        print(f"Phone number {phone_number} not found in any shifts.")


@shift_router.delete("/shifts/{phone_no}")
async def cancel_shift(phone_no: str):
    # Authenticate the sheet
    request_client = authenticate_google_sheets()
    spreadsheet = request_client.open("SSDVolunteers")

    if not is_valid_phone(request_client, phone_no):
        raise HTTPException(status_code=400, detail="phone number is invalid")

    shifts = get_shifts_by_phone_number(phone_no)
    if not shifts:
        raise HTTPException(status_code=400, detail="No shifts found for this phone number")

    for shift in shifts:
        if phone_no in shift["Volunteers"]:
            delete_phone_number_from_row(spreadsheet.worksheet("shifts"), 3, phone_no)


"""
APIs
@shift_router.get("/shifts/{phone}",
         responses={200: {"description": "Found shifts"}, 400: {"description": "Bad request"}},
         summary="Get shifts using phone number",
         response_model= list[dict[str, int | float | str]])
async def get_shifts_by_email_or_phone_number(phone: str):
    print(f"phone_number: {phone}")

    # Authenticate the sheet
    request_client = authenticate_google_sheets()

    if phone is None:
        raise HTTPException(status_code=400, detail="Bad request")

    return get_shifts(request_client, phone)



@shift_router.get("/availableshifts/{phone}",
                  responses={200: {"description": "Get all available shifts"}, 400: {"description": "Bad request"}},
                  summary="Get all available shifts",
                  response_model=list[dict[str, int | float | str]])
async def get_available_shifts(phone: Optional[str] = None):
    print(f"phone: {phone}")

    # Authenticate the sheet
    request_client = authenticate_google_sheets()

    if not is_valid_phone(request_client, phone):
        raise HTTPException(status_code=400, detail="phone number is invalid")

    shifts = get_all_shifts(request_client)
    available_shifts = []

    for shift in shifts:
        if phone not in shift["Volunteers"] and shift["Is Available"] == "Yes":
            available_shifts.append(shift)
    return available_shifts

"""



