from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
app = FastAPI()


# Webhook handler to route requests based on the intent
@app.post("/webhook")
async def webhook_handler(request: Request):
    # Retrieve the JSON data from the request
    payload = await request.json()

    # Get the intent name from the incoming request
    intent_name = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    outputContexts = payload['queryResult']['outputContexts']

    if intent_name == "cancel.volunteer.schedule":
        return JSONResponse(content={"fulfillmentText": "Received {intent_name} in the backend"})

    if intent_name == "new.volunteer":
        return JSONResponse(content={"fulfillmentText": "Received {intent_name} in the backend"})

    if intent_name == "volunteer.add - context: ongoing-signup":
        add_volunteer(parameters)
        return JSONResponse(content={"fulfillmentText": "Received {intent_name} in the backend"})

def add_volunteer(parameters):
    firstName = parameters['firstName']
    lastName = parameters['lastName']
    email = parameters['email']
    phoneNumber = parameters['phoneNumber']
    location = parameters['location']
    print(f"Saving volunteer info: {firstName}, {lastName}, {email}, {phoneNumber}, {location}")

