import time
import traceback
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.http import FileResponse, HttpResponse
from django.urls import reverse_lazy

from schedule import settings

from .models import Job, JobFile, ScheduleUser
from .forms import NewJobForm, UploadJobFileForm, JobForm
from .utils import notify_users_txt
from .checks import groups_required, transcriber_required, admin_required, recipient_required

TZ = ZoneInfo(settings.TIME_ZONE)

# Create your views here.
def index(request):
  return render(request, "core/index.html")

def _txt_helper(request, msg, users=[]):
  try:
    notify_users_txt(msg, users)
    messages.add_message(request, messages.SUCCESS, "Text message sent.")
  except Exception as e:
    messages.add_message(request, messages.ERROR, "There was a problem sending the text message.")
    traceback.print_exc()

def _njob(request, form):
  return render(request, "core/form.html", {
    "form": form
  })

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

@admin_required()
def new_job(request):
  form = NewJobForm()
  if request.method == "POST":
    form = NewJobForm(request.POST, request.FILES)
    if not form.is_valid():
      messages.add_message(request, messages.ERROR, "Invalid form.")
      return _njob(request, form)
    job = None
    try:
# set time due to 00:00 on that day
      due_date = datetime.combine(form.cleaned_data["due_date"], datetime.min.time())
      due_date = due_date.replace(tzinfo=TZ)
      job = Job.objects.create(
        name=form.cleaned_data["name"],
        due_date=due_date,
        status="U", # unclaimed job
        submitter=request.user
      )
    except Exception as e:
      messages.add_message(request, messages.ERROR, "There was an error saving the job. Please contact the administrator.")
      return _njob(request, form)
    try:
      for file in request.FILES.getlist("files"):
        jf = JobFile.objects.create(
          file_type="S", # source material
          job=job,
          file=file
        )
    except Exception as e:
      messages.add_message(request, messages.ERROR, "Error saving uploaded files. Perhaps they are too big?")
    messages.add_message(request, messages.SUCCESS, "New job added.")
    job_name = form.cleaned_data["name"]
    job_due_dt = datetime.combine(form.cleaned_data["due_date"], datetime.min.time())
    job_due_date = _job_due_date(job_due_dt)
    claim_job_url = settings.BASE_URL + reverse_lazy("claim", kwargs={"jobid": job.id})
    _txt_helper(request, f"New job added on https://jobs.bytetools.ca/ named \"{job_name}\" and is due on {job_due_date}. Log in or go to the following URL to claim this job: {claim_job_url}", users=[u for u in ScheduleUser.objects.filter(groups__name="transcriber", new_job_notifications__name="T")]) # T = text
  return _njob(request, form)

@transcriber_required()
def unclaim(request, jobid):
  try:
    job = Job.objects.get(id=jobid)
    job.status = "U" # unclaimed
    job.assigned_to = None
    try:
      job.save()
      messages.add_message(request, messages.SUCCESS, f"Job removed")
    except:
      messages.add_message(request, messages.ERROR, f"Error unclaiming job.")
  except:
    messages.add_message(request, messages.ERROR, f"Job not found")
  return myjobs(request)

@transcriber_required()
def claim(request, jobid):
  job = None
  try:
    job = Job.objects.get(id=jobid)
  except Exception as e:
    messages.add_message(request, messages.ERROR, f"Job not found.")
    return myjobs(request)
  
  if len(request.user.transcriber_jobs.filter(status=["C"])) >= 3:
    messages.add_message(request, messages.ERROR, f"You cannot claim more than 3 jobs at a time.")
    return jobs(request)
  if not job.assigned_to:
    if job.status == "D":
      messages.add_message(request, messages.INFO, f"This job is already complete. You cannot claim it.")
    else:
      job.assigned_to = request.user
      job.status = "C" # claimed 
  else:
    messages.add_message(request, messages.INFO, f"This job is already assigned!")
    return jobs(request)
  try:
    job.save()
    messages.add_message(request, messages.SUCCESS, f"Added to your jobs.")
    return myjobs(request)
  except:
    messages.add_message(request, messages.ERROR, f"Could not save job.")
  return jobs(request)

def _get_job_status(job, now, tmr):
  if job.status == "D": # complete/done
    return "complete"
  else:
    due_date = datetime.combine(job.due_date, datetime.min.time())
    due_date = due_date.replace(tzinfo=TZ)
    if due_date < now:
      return "late"
    elif due_date < tmr:
      return "due"
    else:
      return "on-time"

def _set_job_statuses(jobs):
  now = datetime.now(TZ)
  tmr = now + timedelta(days=1)
  return [{"job": job, "status": _get_job_status(job, now, tmr)} for job in jobs]

def _jobs(request, jobs, done_jobs, header, done_header):
  jobs_str = render_to_string("core/_joblist.html", {
    "jobs": _set_job_statuses(jobs)
  }, request)
  done_jobs_str = render_to_string("core/_joblist.html", {
    "jobs": _set_job_statuses(done_jobs)
  }, request)
  return render(request, "core/joblist.html", {
    "jobs": jobs_str,
    "done_jobs": done_jobs_str,
    "header": header,
    "done_header": done_header,
    "current": datetime.now(TZ),
    "next_day": datetime.now(TZ) + timedelta(days=1),
    "noteworthy": ["late", "due"],
  })

@transcriber_required()
def jobs(request):
  uuids = [job.id for job in Job.objects.all()]
  return _jobs(
    request,
    Job.objects.exclude(status="D").order_by("due_date"),
    Job.objects.filter(status="D").order_by("-due_date"), # D = done
    "Job List",
    "Completed Jobs",
  )

@transcriber_required()
def myjobs(request):
  return _jobs(
    request,
    Job.objects.exclude(status="D").filter(assigned_to=request.user).order_by("due_date"),
    Job.objects.filter(assigned_to=request.user, status="D").order_by("due_date"),
    "My Jobs",
    "Job History",
  )

@transcriber_required()
def upload(request, jobid):

  form = UploadJobFileForm()
  job = None
  try:
    job = Job.objects.get(id=jobid)
    form = UploadJobFileForm(initial={"name": job.name})
  except Exception as e:
    messages.add_message(request, messages.ERROR, "Job not found")
    return redirect(reverse_lazy("myjobs"))
  if request.user != job.assigned_to or not request.user.groups.filter(name="admin").exists():
    messages.add_message(request, messages.ERROR, "You are not the owner of this document.")

  if request.method == "POST":
    form = UploadJobFileForm(request.POST, request.FILES, initial={"name": job.name})
    if form.is_valid():
      try:
        for file in request.FILES.getlist("files"):
          jf = JobFile.objects.create(
            job=job,
            file=file,
            file_type="O" # other files (not complete until marked so)
          )
        messages.add_message(request, messages.SUCCESS, "Job files added.")
        return redirect(reverse_lazy("myjobs"))
      except Exception as e:
        messages.add_message(request, messages.ERROR, "Error saving job file")
    else:
      messages.add_message(request, messages.ERROR, "Invalid form")
  else:
    if request.user != job.assigned_to and not request.user.is_superuser:
# TODO: this is weird since a refresh will cause the same result. This should be a redirect.
      messages.add_message(request, messages.WARNING, f"You are not the claimant of this job.")
      return jobs(request)
  return render(request, "core/form.html", {
    "form": form,
  })

@groups_required("transcriber", "receiver")
def download(request, fileid):
  try:
    file = JobFile.objects.get(id=fileid)
# download file :)
    return FileResponse(file.file, as_attachment=True)
  except:
# TODO: 404
    messages.add_message(request, messages.ERROR, f"File not found")
    return myjobs(request)

@transcriber_required()
def finish(request, jobid):
  job = None
  try:
    job = Job.objects.get(id=jobid)
  except:
    messages.add_message(request, messages.ERROR, "Job not found")
    return myjobs(request)
  if job.status != "C":
    messages.add_message(request, messages.ERROR, f"You cannot finish a job which is either complete, or unclaimed.")
    return myjobs(request)
  
  job.status = "P" # pending review/edits
  try:
    job.save()
    messages.add_message(request, messages.SUCCESS, f"Job is now pending approval.")
  except:
    messages.add_message(request, messages.ERROR, f"Could not save status.")
    return myjobs(request)
  job_due_date = _job_due_date(job.due_date)
  _txt_helper(request, f"The job \"{job.name}\" is pending approval. Please login and review it before the due date, on {job_due_date}.", users=[u for u in ScheduleUser.objects.filter(groups__name="reviewer", job_pending_edits_notifications__name="T")]) # T = text
  return myjobs(request)

@transcriber_required()
def edit(request, jobid):
  job = None
  form = None
  try:
    job = Job.objects.get(id=jobid)
    form = JobForm(instance=job)
  except Exception as e:
    messages.add_message(request, messages.ERROR, f"Job not found")
    return myjobs(request)
  if request.method == "POST":
    form = JobForm(request.POST, request.FILES, instance=job)
    if form.is_valid():
      form.save()
      messages.add_message(request, messages.SUCCESS, f"Job is saved!")
    else:
      messages.add_message(request, messages.ERROR, f"Form is not valid")
  return render(request, "core/form.html", {
    "form": form
  })

@groups_required("reviewer")
def complete(request, jobid):
  job = None
  try:
    job = Job.objects.get(id=jobid)
  except Exception as e:
    messages.add_message(request, messages.ERROR, f"The job is not found.")
    return myjobs(request)
  
  if not job.status == "P": # pending edits/approval
    messages.add_message(request, messages.ERROR, f"The job cannot be completed unless it is current awaiting approval.")
    return myjobs(request)
  
  try:
    job.status = "D" # done/complete
    job.save()
    messages.add_message(request, messages.SUCCESS, f"Job marked as complete.")
  except Exception as e:
    messages.add_message(request, messages.ERROR, f"Job could not be completed.")

  if job.recipient:
    job_completed_notification_types = [j.name for j in job.recipient.job_completed_notifications.all()]
    if "T" in job_completed_notification_types: # T = text
      rec_url = settings.BASE_URL + reverse_lazy("rec_jobs")
      _txt_helper(request, f"Job \"{job.name}\" is complete. Login, or go to this URL to see your documents: {rec_url}", users=[job.recipient])
  return myjobs(request)

# for receiving users
@recipient_required()
def received(request):
  return _jobs(
    request,
    Job.objects.filter(recipient=request.user, status="D").order_by("-due_date"),
    Job.objects.exclude(status="D").filter(recipient=request.user).order_by("due_date"),
    "Completed Work",
    "In Progress",
  )
