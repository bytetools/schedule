import traceback
from phonenumber_field.phonenumber import PhoneNumber
from .models import Job, ScheduleUser
from .twilio import send_text_to

class TextMessageException(Exception):
  pass

def notify_users_txt(msg, users=[]):
  """
  Notify users who have text notifications turned on with {msg}.
  """
  errors = []
  for user in users:
    if user.phone:
      try:
        send_text_to(user.phone.as_e164, msg)
      except Exception as e:
        traceback.print_exc()
        errors.append("".join(traceback.format_stack()))
  if len(errors) != 0:
    raise TextMessageException("\n".join(errors))
