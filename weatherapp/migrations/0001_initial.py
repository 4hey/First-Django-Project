# Generated by Django 3.0.2 on 2020-02-25 21:50

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='WeatherModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prefecture', models.CharField(max_length=10)),
                ('city', models.CharField(max_length=50)),
            ],
        ),
    ]