# Generated by Django 4.0.3 on 2022-04-20 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_notificationtype_scheduleuser_new_job_notifications'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scheduleuser',
            name='new_job_notifications',
            field=models.ManyToManyField(blank=True, default=[], related_name='users', to='core.notificationtype'),
        ),
    ]