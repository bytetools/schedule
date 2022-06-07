import traceback
from phonenumber_field.phonenumber import PhoneNumber
from discord_webhook import DiscordWebhook
from django.conf import settings
from django.urls import reverse_lazy
from .models import Job, ScheduleUser
from .twilio import send_text_to

def _make_ordinal(n):
    '''
    Convert an integer into its ordinal representation::

        make_ordinal(0)   => '0th'
        make_ordinal(3)   => '3rd'
        make_ordinal(122) => '122nd'
        make_ordinal(213) => '213th'

    From: https://stackoverflow.com/questions/9647202/ordinal-numbers-replacement
    '''
    n = int(n)
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    return str(n) + suffix

def _job_due_date(dt):
  job_due_date_day_ordinal = _make_ordinal(dt.day)
  return dt.strftime(f"%A, %B {job_due_date_day_ordinal} %Y")

def job_info_dict(job):
  return {
    "job_name": job.name,
    "claim_job_url": settings.BASE_URL + reverse_lazy("claim", kwargs={"jobid": job.id}),
    "due_date": _job_due_date(job.due_date)
  }

def create_new_text_msg(job):
  info = job_info_dict(job)
  return f"New job added on {settings.BASE_URL} named \"{info['job_name']}\" and is due on {info['due_date']}. Log in or click the following URL to claim this job: {info['claim_job_url']}"

def create_new_discord_msg(job):
  info = job_info_dict(job)
  return f"<@&{settings.DISCORD_NEW_JOB_NOTIFICATION_ROLE_ID}> New job added on {settings.BASE_URL} named \"{info['job_name']}\" and is due on {info['due_date']}. Log in or click the following URL to [claim this job]({info['claim_job_url']})"

def create_review_discord_msg(job):
    info = job_info_dict(job)
    return f"<@&{settings.DISCORD_REVIEW_JOB_NOTIFICATION_ROLE_ID}> The job \"{job.name}\" is pending approval. Please login and review it before the due date, on {info['due_date']}."

def discord_new_job(job):
    webhook = DiscordWebhook(
      url=settings.DISCORD_NEW_JOB_WEBHOOK_URL,
      content=create_new_discord_msg(job))
    webhook.execute()

def discord_review_job(job):
    webhook = DiscordWebhook(
      url=settings.DISCORD_REVIEW_JOB_WEBHOOK_URL,
      content=create_review_discord_msg(job))
    webhook.execute()

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
