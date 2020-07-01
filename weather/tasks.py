from __future__ import absolute_import, unicode_literals
from celery import shared_task
from celery.task.control import revoke
from weather.celery import app
from django.core.mail import send_mail
from django.core import mail
from django.template.loader import render_to_string
import datetime
import time
from weatherapp.models import Schedule, WeatherForecast, ProbabilityOfRain
from accounts.models import User
from weather import settings

import requests
from bs4 import BeautifulSoup
import re


@shared_task
def sender(user_id, schedule_id, information):

    user = User.objects.get(id=user_id)

    if schedule_id == None:
        schedule = Schedule.objects.all()[0]
    else:
        schedule = Schedule.objects.get(id=schedule_id)

    if  information == None:
        weather = None
        prob_rains = None
    else:
        if information == 24.0:
            how_many_days_latter = 1
        else:
            how_many_days_latter = 0
        weather = WeatherForecast.objects.get(
            city=User.c_choices[user.city][1],
            how_many_days_latter=how_many_days_latter
        ).weather

        schedule_times = [int(schedule.start), int(schedule.end)]
        now =datetime.datetime.now()
        now = (now.hour * 60 * 60 + now.minute * 60 + now.second) / 3600
        fixed_schedule_times = []
        for schedule_time in schedule_times:
            split_time = Schedule.time_choices[schedule_time][1].split(':')
            if split_time[1] == '30':
                hour = float(split_time[0]+'.5')
            else:
                hour = float(split_time[0])
            if information != 24.0 and hour < now:
                hour = now
            fixed_schedule_times.append(hour)

        hour_list = []
        if fixed_schedule_times[0] == fixed_schedule_times[1]:
            for i in [(18, '18-24'), (12, '12-18'), (6, '6-12'), (0, '0-6')]:
                if i[0] <= fixed_schedule_times[1]:
                    hour_list.append(i[1])
                    break
        else:
            for i in [(0, '0-6'), (6, '6-12'), (12, '12-18'), (18, '18-24')]:
                if i[0] < fixed_schedule_times[1]:
                    hour_list.append(i[1])
            for i in [(6, '0-6'), (12, '6-12'), (18, '12-18'), (24, '18-24')]:
                if i[0] <= fixed_schedule_times[0]:
                    del hour_list[0]

        prob_rains = []
        for hour in hour_list:
            prob_rain = ProbabilityOfRain.objects.get(
                city=User.c_choices[user.city][1],
                hour=hour,
                day=how_many_days_latter
            )
            prob_rains.append(prob_rain)

    context = {
        'user':user,
        'schedule':schedule,
        'weather':weather,
        'prob_rains':prob_rains
    }

    subject = '【weatherapp】登路された予定があります'
    message = render_to_string('weatherapp/mail_message.txt', context)
    from_email = 'information@weatherapp'
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)
    print('Send email to \"' + mail.outbox[-1].to[0] + '\"')
    print('subject:', mail.outbox[-1].subject)
    print('message:', mail.outbox[-1].body)


@shared_task
def save_task_id(task_id, schedule_id):
    if schedule_id == None:
        schedule = Schedule.objects.all()[0]
    else:
        schedule = Schedule.objects.get(id=schedule_id)

    if schedule.task_id:
        app.control.revoke(schedule.task_id, terminate=True)

    if task_id:
        schedule.task_id = task_id
        schedule.save()


@shared_task
def weather_forecast():
    print('runnning: weather_forecast')
    r = requests.get('https://weather.yahoo.co.jp/weather/')
    s = BeautifulSoup(r.text, 'html.parser')

    text = re.compile('^//weather.yahoo.co.jp/weather/jp/.{1,2}/')
    pref_list = s.find_all('a', href=text)
    for pref in pref_list:
        pref_name = str(pref.string)
        print(pref_name)
        pref_url = 'https:' + pref['href']

        r = requests.get(pref_url)
        s = BeautifulSoup(r.text, 'html.parser')
        text=re.compile('.html$')
        city_list = s.find_all('a', class_='rapidnofollow', href=text)
        for i in city_list:
            city_name = str(i.dt.string)
            print(city_name)
            city_url = i['href']

            r = requests.get(city_url)
            s = BeautifulSoup(r.text, 'html.parser')
            text = re.compile('day.png$|night.png$')
            weather_list = s.find_all('img', src=text)
            for i, weather in enumerate(weather_list):
                defaults = {
                    'prefecture':pref_name,
                    'city':city_name,
                    'how_many_days_latter':i,
                    'weather':weather['alt'],
                }
                kwargs = {
                    'prefecture':pref_name,
                    'city':city_name,
                    'how_many_days_latter':i,
                }
                WeatherForecast.objects.update_or_create(defaults=defaults, **kwargs)
    print('Done!!')


@shared_task
def probability_of_rain():
    print('runnning: probability_of_rain')
    r = requests.get('https://weather.yahoo.co.jp/weather/')
    s = BeautifulSoup(r.text, 'html.parser')

    text = re.compile('^//weather.yahoo.co.jp/weather/jp/.{1,2}/')
    pref_list = s.find_all('a', href=text)
    for pref in pref_list:
        pref_name = str(pref.string)
        print(pref_name)
        pref_url = 'https:' + pref['href']

        r = requests.get(pref_url)
        s = BeautifulSoup(r.text, 'html.parser')
        text=re.compile('.html$')
        city_list = s.find_all('a', class_='rapidnofollow', href=text)
        for i in city_list:
            city_name = str(i.dt.string)
            print(city_name)
            city_url = i['href']

            r = requests.get(city_url)
            s = BeautifulSoup(r.text, 'html.parser')
            rain_list = s.find_all('tr', class_='precip')
            hour_list = s.find_all('tr', class_='time')
            for i in range(2):
                for r, h in zip(rain_list[i].stripped_strings, hour_list[i].stripped_strings):
                    if r == '降水':
                        continue
                    else:
                        defaults = {
                            'prefecture':pref_name,
                            'city':city_name,
                            'hour':h,
                            'day':i,
                            'prob_rain':r
                        }
                        kwargs = {
                            'prefecture':pref_name,
                            'city':city_name,
                            'hour':h,
                            'day':i
                        }
                        ProbabilityOfRain.objects.update_or_create(defaults=defaults, **kwargs)
    print('Done!!')
