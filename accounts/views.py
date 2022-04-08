import traceback
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .forms import UserForm

# Create your views here.
@login_required
def profile(request):
  return render(request, "accounts/profile.html")

def _eform(request, form):
  return render(request, "core/form.html", {
    "form": form,
  })

@login_required
def edit(request):
  form = UserForm(instance=request.user)
  if request.method == "POST":
    form = UserForm(request.POST, instance=request.user)
    if not form.is_valid():
      messages.add_message(request, messages.ERROR, f"Invalid form request.")
      return _eform(request, form) 
    try:
      form.save()
      messages.add_message(request, messages.SUCCESS, f"Profile saved.")
    except:
      traceback.print_exc()
      messages.add_message(request, messages.ERROR, f"There was an error saving your info.")

  return _eform(request, form)
