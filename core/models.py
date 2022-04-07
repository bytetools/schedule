from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class ScheduleUser(AbstractUser):
  pass

# Create your models here.
class Institution(models.Model):
  name = models.CharField(max_length=64, null=False, blank=False)
# generally an abbreviation
  short_name = models.CharField(max_length=10, null=False, blank=False)

  def __str__(self):
    return f"{self.name}"

# good for sorting in the future; e.g., get all jobs from one course, one institution, etc.
class Tag(models.Model):
  name = models.CharField(max_length=32, null=False, blank=False)

class Job(models.Model):
  name = models.CharField(max_length=32, null=False, blank=False)
  STATUS_CHOICES = (
    ("U", "Unclaimed"), # new jobs
    ("C", "Claimed"), # claimed by contractor
    ("P", "Pending Edits/Approval"), # contractor is done, but QA/math/tables/diagrams may be necessary
    ("D", "Done"), # complete and done
  )
  institution = models.ForeignKey(Institution, on_delete=models.PROTECT, related_name="jobs", null=False, blank=False)
# the time when this file must be completed by: this includes time so that a student can receive it the morning of if necessary
  due_date = models.DateTimeField(null=False, blank=False)
  status = models.CharField(max_length=1, choices=STATUS_CHOICES, blank=False, null=False)
  assigned_to = models.ForeignKey(ScheduleUser, on_delete=models.PROTECT, related_name="jobs", blank=True, null=True)
  tags = models.ManyToManyField(Tag, related_name="jobs", blank=True)

  def __str__(self):
    return f"{self.name}"

class JobFile(models.Model):
  file = models.FileField(upload_to="uploads/%Y/%m/%d/")
  job = models.ForeignKey(Job, on_delete=models.PROTECT, related_name="files", null=False, blank=False)

  def filename(self):
# always get last part of file name
    try:
      fname = self.file.name.split("/")[-1:][0]
    except:
      fname = ""
    return f"{fname}"
