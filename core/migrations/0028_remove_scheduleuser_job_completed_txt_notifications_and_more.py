# Generated by Django 4.0.3 on 2022-05-06 17:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_alter_notificationtype_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scheduleuser',
            name='job_completed_txt_notifications',
        ),
        migrations.RemoveField(
            model_name='scheduleuser',
            name='job_pending_edits_txt_notifications',
        ),
        migrations.RemoveField(
            model_name='scheduleuser',
            name='new_job_txt_notifications',
        ),
    ]