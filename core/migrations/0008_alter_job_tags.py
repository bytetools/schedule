# Generated by Django 4.0 on 2022-04-04 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_job_assigned_to_alter_job_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='jobs', to='core.Tag'),
        ),
    ]
