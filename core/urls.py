from django.urls import path, include
from . import views

urlpatterns = [
  path("", views.index, name="home"),
  path("jobs/", views.jobs, name="joblist"),
  path("jobs/new/", views.new_job, name="newjob"),
  path("jobs/claim/<jobid>/", views.claim, name="claim"),
  path("jobs/myjobs/", views.myjobs, name="myjobs"),
  path("jobs/submit/<jobid>/", views.upload, name="upload"),
  path("jobs/unclaim/<jobid>/", views.unclaim, name="unclaim"),
  path("jobs/finish/<jobid>/", views.finish, name="finish"),
  path("jobs/downloads/<fileid>/", views.download, name="download_file"),
  path("", include("django.contrib.auth.urls")),
]
