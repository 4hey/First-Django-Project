from django.db import models
from django.core import validators
import datetime
from accounts.models import User

class Schedule(models.Model):

    this_year = int(datetime.date.today().strftime('%Y'))

    time_choices = []
    num = (i for i in range(48))
    for a in range(24):
        time_choices.append((str(next(num)), str(a)+":00"))
        time_choices.append((str(next(num)), str(a)+":30"))

    information_choices = [
        ('0.5', '30分前'), ('1', '1時間前'), ('2', '2時間前'), ('3', '3時間前'),
        ('6', '6時間前'), ('12', '12時間前'), ('24', '24時間前')
    ]

    year = models.IntegerField(default=this_year, validators=[
        validators.MinValueValidator(this_year, message='無効な値です')
        ])
    month = models.IntegerField(default=1, validators=[
        validators.MinValueValidator(1, message='無効な値です'),
        validators.MaxValueValidator(12, message='無効な値です')
        ])
    day = models.IntegerField(default=1, validators=[
        validators.MinValueValidator(1, message='無効な値です'),
        validators.MaxValueValidator(31, message='無効な値です')
        ])
    title = models.CharField(max_length=50)
    detail = models.CharField(max_length=200)
    start = models.CharField(max_length=2, choices=time_choices, default='0')
    end = models.CharField(max_length=2, choices=time_choices, default='1')
    information = models.CharField(max_length=3, choices=information_choices, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task_id = models.CharField(max_length=36, blank=True)

    def __str__(self):
        return self.title


class WeatherForecast(models.Model):

    prefecture = models.CharField(max_length=3)
    city = models.CharField(max_length=4)
    how_many_days_latter = models.IntegerField()
    weather = models.CharField(max_length=5)

    def __str__(self):
        return self.city + str(self.how_many_days_latter)

class ProbabilityOfRain(models.Model):

    prefecture = models.CharField(max_length=3)
    city = models.CharField(max_length=4)
    hour = models.CharField(max_length=5)
    prob_rain = models.CharField(max_length=3)
    day = models.IntegerField()

    def __str__(self):
        return self.city + str(self.day) + '(' + self.hour + ')'
