# app/__init__.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .shift_api import get_shifts_by_phone_number, get_available_shifts
from app.volunteer_api import volunteer_router as volunteer
from app.shift_api import shift_router as shift

app = FastAPI()

app.include_router(volunteer)
app.include_router(shift)

@app.post("/")
async def dialogflow_webhook(request: Request):
    req = await request.json()
    intent = req["queryResult"]["intent"]["displayName"]
    print("inside dialogflow webhook")

    if intent == "GetVolunteerShifts":
        phone = req["queryResult"]["parameters"].get("phone-number")
        my_shifts = get_shifts_by_phone_number(req["queryResult"]["parameters"].get("phone-number"))
        print(my_shifts)
        return JSONResponse(content={ "fulfillmentText": f"shifts: {my_shifts}"
        })

    elif intent == "GetAvailableShifts":
        phone = req["queryResult"]["parameters"].get("phone-number")
        open_shifts = get_available_shifts(req["queryResult"]["parameters"].get("phone-number"))
        print(open_shifts)

        # Build human-readable fallback text
        fallback_lines = ["📅 Available Shifts:\n"]
        for shift in open_shifts:
            fallback_lines.append(
                f"🕒 {shift['Shift Date']} — {shift['Start Time']} to {shift['End Time']}\n"
            )
        fallback_text = "\n".join(fallback_lines)
        rich_content = [
           [
               {
                   "type": "card",
                   "title": f"Shift on {shift['Shift Date']}",
                   "subtitle": f"From {shift['Start Time']} to {shift['End Time']}",
                   "buttons": [
                       {
                           "text": f"Sign up for {shift['Shift Date']}",
                           "postback": f"https://yourdomain.com/signup?date={shift['Shift Date']}&start={shift['Start Time']}"
                       }
                   ]
                }
                for shift in open_shifts
           ]
        ]

        # Create the response structure
        response_data = {
              "fulfillmentMessages": [
                {
                  "text": {
                    "text":[fallback_text]
                  }
                },
                {
                  "payload": {
                    "richContent": rich_content
                  }
                }
              ]
            }

        return JSONResponse(content=response_data)




"""
from app.volunteer_api import volunteer_router as volunteer
from app.shift_api import shift_router as shift
from app.dialogflow_webhook import dialogflow_router as dialogflow_webhook

#app.include_router(volunteer)
#app.include_router(shift)
#app.include_router(dialogflow_webhook)

"""
