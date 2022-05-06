from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget
from django.contrib.auth import get_user_model
from django.forms import widgets
from django import forms

class UserForm(forms.ModelForm):
  template_name = "accounts/profile_forms.html"
  class Meta:
    fields = ["email", "phone", "new_job_notifications", "job_pending_edits_notifications", "job_completed_notifications"]
    model = get_user_model()
    widgets = {
      "phone": PhoneNumberInternationalFallbackWidget(),
    }
    labels = {
      "new_job_notifications": "Get text message when new jobs are posted (only for transcribers)",
      "job_pending_edits_notifications": "Get text messages when a job is pending approval (only for reviewers)",
      "job_completed_notifications": "Get text messages when a job is completed (only for clients, recipients)",
    }

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    groups = [x["name"] for x in self.instance.groups.values()] # ("id": 1, "name": "transcriber"} -> "transcriber"
    print(groups)
    if not "transcriber" in groups:
      self.fields["new_job_notifications"].widget.attrs["disabled"] = True
    if not "reviewer" in groups:
      self.fields["job_pending_edits_notifications"].widget.attrs["disabled"] = True
    if not "recipient" in groups:
      self.fields["job_completed_notifications"].widget.attrs["disabled"] = True

