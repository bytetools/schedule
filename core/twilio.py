from twilio.rest import Client

TWILIO_SID = "ACc96f833804267972fed344d2f53fc54d"
TWILIO_AUTH = "2da91aadf36211297dd252bb63af95e6"
TWILIO_NUM = "+17126256069"

client = Client(TWILIO_SID, TWILIO_AUTH)

def send_text_to(number, msg):
  message = client.messages.create(
    to=number,
    from_=TWILIO_NUM,
    body=msg
  )
  print(message.sid)
