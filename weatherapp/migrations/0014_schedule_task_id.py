# Generated by Django 3.0.3 on 2020-05-19 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weatherapp', '0013_probabilityofrain_day'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='task_id',
            field=models.CharField(blank=True, max_length=36),
        ),
    ]
