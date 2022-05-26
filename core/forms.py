from datetime import date
from .models import Job
from django import forms
from django.forms import widgets

class NewJobForm(forms.Form):
  name = forms.CharField()
  due_date = forms.DateField(widget=widgets.SelectDateWidget())
  files = forms.FileField(widget=forms.ClearableFileInput(attrs={"multiple": True}))
  notify_transcribers = forms.BooleanField(required=False)

class UploadJobFileForm(forms.Form):
  name = forms.CharField(required=False, widget=forms.TextInput(attrs={"disabled": True}))
  files = forms.FileField(widget=forms.ClearableFileInput(attrs={"multiple": True}))

class JobForm(forms.ModelForm):
  class Meta:
    exclude = []
    model = Job
