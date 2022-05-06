from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test

def groups_required(*group_names):
  """
  Requires user membership in at least one of the groups passed in.

  """

  def in_groups(u):
    if u.is_authenticated:
      if u.is_superuser or bool(u.groups.filter(name__in=group_names)):
        return True
    return False
  return user_passes_test(in_groups, login_url=reverse_lazy("home"))

def transcriber_required():
  return groups_required("transcriber", "admin")

def client_required():
  return groups_required("client", "admin")

def recipient_required():
  return groups_required("recipient", "admin")

def admin_required():
  return groups_required("admin")
