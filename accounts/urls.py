from . import views
from django.urls import path, include

urlpatterns = [
  path("profile/", views.profile, name="profile"),
  path("edit/", views.edit, name="edit_profile"),
  path("", include("django.contrib.auth.urls")),
]
