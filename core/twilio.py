import os
from dotenv import load_dotenv, find_dotenv
from twilio.rest import Client

load_dotenv(find_dotenv())

TWILIO_SID = os.environ["TWILIO_SID"]
TWILIO_AUTH = os.environ["TWILIO_AUTH"]
TWILIO_NUM = os.environ["TWILIO_NUM"]

client = Client(TWILIO_SID, TWILIO_AUTH)

def send_text_to(number, msg):
  message = client.messages.create(
    to=number,
    from_=TWILIO_NUM,
    body=msg
  )
  print(message.sid)
