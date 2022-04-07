from .models import Job
from django import forms

class NewJobForm(forms.ModelForm):
  class Meta:
    exclude = []
    model = Job

class UploadJobFileForm(forms.Form):
  files = forms.FileField(widget=forms.ClearableFileInput(attrs={"multiple": True}))
