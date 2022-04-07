from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import FileResponse, HttpResponse

from schedule import settings

from .models import Job, JobFile
from .forms import NewJobForm, UploadJobFileForm

TZ = ZoneInfo(settings.TIME_ZONE)

# Create your views here.
def index(request):
  return render(request, "core/index.html")

@login_required
def new_job(request):
  return render(request, "core/form.html", {
    "form": NewJobForm(),
  })

@login_required
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

@login_required
def claim(request, jobid):
  try:
    job = Job.objects.get(id=jobid)
    if len(request.user.jobs.all()) >= 3:
      messages.add_message(request, messages.ERROR, f"You cannot claim more than 3 jobs at a time.")
      return jobs(request)
    if not job.assigned_to:
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
  except:
    messages.add_message(request, messages.ERROR, f"Could not find the job.")
  return jobs(request)

def _get_job_status(job, now, tmr):
  if job.status == "D": # complete/done
    return "complete"
  else:
    if job.due_date < now:
      return "late"
    elif job.due_date < tmr:
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

@login_required
def jobs(request):
  return _jobs(
    request,
    Job.objects.exclude(status="D").order_by("due_date"),
    Job.objects.filter(status="D").order_by("due_date"), # D = done
    "Job List",
    "Done Job List",
  )

@login_required
def myjobs(request):
  return _jobs(
    request,
    Job.objects.exclude(status="D").filter(assigned_to=request.user).order_by("due_date"),
    Job.objects.filter(assigned_to=request.user, status="D").order_by("due_date"),
    "My Jobs",
    "My Done Jobs",
  )

@login_required
def upload(request, jobid):
  job = Job.objects.get(id=jobid)
  if request.user != job.assigned_to and not request.user.is_superuser:
    messages.add_message(request, messages.WARNING, f"You are not the claimant of this job.")
    return jobs(request)
  return render(request, "core/form.html", {
    "form": UploadJobFileForm(),
  })

@login_requred
def download(request, fileid):
  try:
    file = JobFile.objects.get(id=fileid)
# download file :)
    return FileResponse(file.file, as_attachment=True)
  except:
# TODO: 404
    messages.add_message(request, messages.ERROR, f"File not found")
    return myjobs(request)

@login_required
def finish(request, jobid):
  try:
    job = Job.objects.get(id=jobid)
    job.status = "P" # pending review/edits
    try:
      job.save()
      messages.add_message(request, messages.SUCCESS, f"Job is now pending approval.")
    except:
      messages.add_message(request, messages.ERROR, f"Could not save status.")
  except:
    messages.add_message(request, messages.ERROR, f"Job not found")
  return myjobs(request)
