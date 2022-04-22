from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group
from core.models import NotificationType

class Command(BaseCommand):
  help = 'Populate database with basic types like NotificationTypes and user groups.'

  def load_notification_types(self):
    types = ["T", "E"]
    for t in types:
      notification_type, _new = NotificationType.objects.get_or_create(name=t)
      if _new:
        self.stdout.write(self.style.SUCCESS(f"Added NotificationType(name=\"{t}\")."))
      else:
        self.stdout.write(self.style.WARNING(f"NotificationType(name=\"{t}\") alread in database."))

  def load_groups(self):
    groups = ["transcriber", "admin", "client", "recipient", "reviewer"]
    for g in groups:
      group, _new = Group.objects.get_or_create(name=g)
      if _new:
        self.stdout.write(self.style.SUCCESS(f"Added group \"{g}\""))
      else:
        self.stdout.write(self.style.WARNING(f"Group \"{g}\" already in database."))

  def handle(self, *args, **kwargs):
    self.stdout.write("Initializing database... ")
    self.load_groups()
    self.stdout.write(self.style.SUCCESS("Successfully populated groups."))
    self.load_notification_types()
    self.stdout.write(self.style.SUCCESS('Successfully populated notification types.'))
