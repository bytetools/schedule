from .models import Institution, Job, JobFile, Tag, ScheduleUser
from django.contrib import admin

# Register your models here.
@admin.register(ScheduleUser)
class ScheduleUserAdmin(admin.ModelAdmin):
  list_display = ["username", "email"]
  search_fields = ["username", "email"]

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
  list_display = ["name", "due_date"]
  search_fields = ["name", "due_date"]

@admin.register(JobFile)
class JobFileAdmin(admin.ModelAdmin):
  list_display = ["job", "file"]
  search_fields = ["job", "file"]

@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
  list_display = ["name"]
  search_fields = ["name"]

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
  list_display = ["name"]
  search_fields = ["name"]
