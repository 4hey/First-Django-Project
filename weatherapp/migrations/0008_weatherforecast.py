# Generated by Django 3.0.3 on 2020-04-13 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weatherapp', '0007_auto_20200318_0628'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeatherForecast',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prefecture', models.CharField(max_length=3)),
                ('city', models.CharField(max_length=4)),
                ('how_many_days_latter', models.IntegerField()),
                ('weather', models.CharField(max_length=5)),
            ],
        ),
    ]
