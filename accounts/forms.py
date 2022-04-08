from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget
from django.contrib.auth import get_user_model
from django import forms

class UserForm(forms.ModelForm):
  class Meta:
    fields = ["email", "phone"]
    model = get_user_model()
    widgets = {
      "phone": PhoneNumberInternationalFallbackWidget()
    }
