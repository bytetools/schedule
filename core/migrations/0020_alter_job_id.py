# Generated by Django 4.0.3 on 2022-04-20 00:44

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_alter_job_due_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
