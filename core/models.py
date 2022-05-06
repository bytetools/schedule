import uuid

from datetime import date

from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class NotificationType(models.Model):
  NOTIFICATION_CHOICES = [
    ("T", "Text Message"),
    ("E", "Email"),
    #("S", "Signal"),
    #("W", "WhatsApp"),
  ]
  name = models.CharField(max_length=1, blank=False, null=False, editable=False)
  def __str__(self):
    for (k,v) in self.NOTIFICATION_CHOICES:
      if k == self.name:
        return v
    return "N/A"

class ScheduleUser(AbstractUser):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  phone = PhoneNumberField(blank=True, null=True)
# only for transcribers
  new_job_notifications = models.ManyToManyField(NotificationType, default=[], blank=True, related_name="new_job_users")
# only for admins
  job_pending_edits_notifications = models.ManyToManyField(NotificationType, default=[], blank=True, related_name="review_users")
# only for recipients
  job_completed_notifications = models.ManyToManyField(NotificationType, default=[], blank=True, related_name="completed_users")

# Create your models here.
class Institution(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  name = models.CharField(max_length=64, null=False, blank=False)
# generally an abbreviation
  short_name = models.CharField(max_length=10, null=False, blank=False)

  def __str__(self):
    return f"{self.name}"

# good for sorting in the future; e.g., get all jobs from one course, one institution, etc.
class Tag(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  name = models.CharField(max_length=32, null=False, blank=False)

class Job(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  name = models.CharField(max_length=32, null=False, blank=False)
  STATUS_CHOICES = (
    ("U", "Unclaimed"), # new jobs
    ("C", "Claimed"), # claimed by contractor
    ("P", "Pending Edits/Approval"), # contractor is done, but QA/math/tables/diagrams may be necessary
    ("D", "Done"), # complete and done
  )
  #institution = models.ForeignKey(Institution, on_delete=models.PROTECT, related_name="jobs", null=False, blank=False)
  submitter = models.ForeignKey(ScheduleUser, on_delete=models.PROTECT, related_name="submitted_jobs", null=True, blank=False)
  recipient = models.ForeignKey(ScheduleUser, on_delete=models.PROTECT, related_name="recieving_jobs", null=True, blank=False)
# the time when this file must be completed by: this includes time so that a student can receive it the morning of if necessary
  due_date = models.DateTimeField(null=False, blank=False)
  status = models.CharField(max_length=1, choices=STATUS_CHOICES, blank=False, null=False)
  assigned_to = models.ForeignKey(ScheduleUser, on_delete=models.PROTECT, related_name="transcriber_jobs", blank=True, null=True)
  tags = models.ManyToManyField(Tag, related_name="jobs", blank=True)

  def __str__(self):
    return f"{self.name}"

class JobFile(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  FILE_TYPE_CHOICES = [
    ("S", "Source Material"),
    ("C", "Completed Material"),
    ("O", "Other Material"),
  ]
  file = models.FileField(upload_to="uploads/%Y/%a/%d/%h:%m:%s/")
  job = models.ForeignKey(Job, on_delete=models.PROTECT, related_name="files", null=False, blank=False)
  file_type = models.CharField(max_length=1, choices=FILE_TYPE_CHOICES, default="S")

  def filename(self):
# always get last part of file name
    try:
      fname = self.file.name.split("/")[-1:][0]
    except:
      fname = ""
    return f"{fname}"
