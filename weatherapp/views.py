from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db.models import Max
from weather import tasks
from .models import Schedule, WeatherForecast
from .forms import ScheduleForm

from weather.celery import app

import requests
from bs4 import BeautifulSoup
import re
import datetime
from dateutil.relativedelta import relativedelta
import calendar
import uuid
from faker import Faker


class UserMatchMixin(UserPassesTestMixin):

    raise_exception = True

    def test_func(self):
        user = self.request.user
        obj = get_object_or_404(Schedule, id=self.kwargs['pk'])
        return user.pk == obj.user.id or user.is_superuser


class ScheduleListView(ListView):
    model = Schedule
    template_name = 'weatherapp/home.html'
    context_object_name = 'month_schedule'

    def get(self, request, *args, **kwargs):

        self.weekdays = ['月','火','水','木','金','土','日']
        today = datetime.date.today()
        self.current_year = int(today.strftime('%Y'))
        self.current_month = int(today.strftime('%-m'))
        self.current_day = int(today.strftime('%-d'))
        self.days =[]
        td_day = datetime.timedelta(days=1)
        for i in range(8):
             day = today + i*td_day
             day = day.strftime('%-m月%-d日')
             self.days.append(day)

        td_month = relativedelta(months=1)
        if self.request.GET:
            if self.request.GET.get('year'):
                year = self.request.GET.get('year')
            if self.request.GET.get('pre'):
                month = self.request.GET.get('pre')
                year_month = datetime.datetime.strptime(year+'/'+month, '%Y/%m')
                self.indicative_year = int(datetime.datetime.strftime(year_month-td_month, '%Y'))
                self.indicative_month = int(datetime.datetime.strftime(year_month-td_month, '%m'))
            if self.request.GET.get('post'):
                month = request.GET.get('post')
                year_month = datetime.datetime.strptime(year+'/'+month, '%Y/%m')
                self.indicative_year = int(datetime.datetime.strftime(year_month+td_month, '%Y'))
                self.indicative_month = int(datetime.datetime.strftime(year_month+td_month, '%m'))
            if request.GET.get('month'):
                self.indicative_month = int(request.GET.get('month'))
                self.indicative_year = int(year)
            if request.GET.get('day'):
                self.indicative_day = int(request.GET.get('day'))
            else:
                self.indicative_day = 1
        else:
            self.indicative_year = self.current_year
            self.indicative_month = self.current_month
            self.indicative_day = self.current_day

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #天気予報
        if self.request.user.is_authenticated:
            pref_key = self.request.user.get_prefecture_display()
            city_key = self.request.user.get_city_display()
        else:
            pref_key = '東京'
            city_key = '東京'

        weather_list = WeatherForecast.objects.filter(prefecture=pref_key, city=city_key)
        weather = []
        for i in weather_list:
            weather.append(i.weather)
        todays_weather = weather[0]


        #カレンダー
        ca = calendar.Calendar(firstweekday=0)
        week_list = ca.monthdayscalendar(self.indicative_year, self.indicative_month)

        context.update(
            prefecture=pref_key,
            city=city_key,
            weather=weather,
            todays_weather=todays_weather,
            days=self.days,
            week_list=week_list,
            weekdays=self.weekdays,
            current_year=self.current_year,
            current_month=self.current_month,
            current_day=self.current_day,
            indicative_year=self.indicative_year,
            indicative_month=self.indicative_month,
            indicative_day=self.indicative_day
        )

        return context

    def get_queryset(self):
        queryset = None
        if self.request.user.is_authenticated:
            queryset = Schedule.objects.filter(
                year=self.indicative_year,
                month=self.indicative_month,
                user=self.request.user.id
            )
        return queryset


class ScheduleDetailView(UserMatchMixin, DetailView):
    model= Schedule


class ScheduleCreateView(LoginRequiredMixin, CreateView):
    model = Schedule
    form_class = ScheduleForm
    login_url = reverse_lazy('login')

    def get_success_url(self):
        return reverse_lazy('weatherapp:home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            initial = {
                'year':int(self.request.GET.get('year')),
                'month':int(self.request.GET.get('month')),
                'day':int(self.request.GET.get('day')),
                'user':self.request.user.id
                }

            form = ScheduleForm(initial=initial)
            context['form'] = form
        return context

    def form_valid(self, form):
        messages.success(self.request, '保存しました')
        try:
            information = float(self.request.POST.get('information'))
            user_id = self.request.user.id
            try:
                schedule_id = list(Schedule.objects.all())[-1].id + 1
            except IndexError:
                schedule_id = None

            today = datetime.datetime.now()
            year = self.request.POST.get('year')
            month = self.request.POST.get('month')
            day = self.request.POST.get('day')

            start_index = int(self.request.POST.get('start'))
            start_time = Schedule.time_choices[start_index][1]
            schedule_start = year + month + day + start_time
            schedule_start = datetime.datetime.strptime(schedule_start, '%Y%m%d%H:%M')
            start_delta = schedule_start - today

            end_index = int(self.request.POST.get('end'))
            end_time = Schedule.time_choices[end_index][1]
            schedule_end = year + month + day + end_time
            schedule_end = datetime.datetime.strptime(schedule_end, '%Y%m%d%H:%M')
            end_delta = schedule_end - today
            end_delta = end_delta.days * 24 * 60 * 60 + end_delta.seconds

            if end_delta <= 0:
                delta = 2
                information =None
            else:
                delta = ((start_delta.days * 24) - information) * 60 * 60 + start_delta.seconds
                if delta <= 0:
                    delta = 2

            try:
                if settings.CELERY_TASK_ALWAYS_EAGER:
                    fake = Faker()
                    Faker.seed(8282)
                    task_id = fake.uuid4()
            except AttributeError:
                task_id = str(uuid.uuid4())

            tasks.sender.apply_async(
                kwargs={'user_id':user_id, 'schedule_id':schedule_id, 'information':information},
                countdown=delta,
                task_id=task_id
            )

            tasks.save_task_id.apply_async(
                kwargs={'task_id':task_id, 'schedule_id':schedule_id},
                countdown=1
            )

        except ValueError:
            pass
        return super().form_valid(form)


class ScheduleUpdateView(UserMatchMixin, UpdateView):
    model = Schedule
    form_class = ScheduleForm
    login_url = reverse_lazy('login')

    def get_success_url(self):
        return reverse_lazy('weatherapp:home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['update'] = True
        return context

    def form_valid(self, form):
        messages.success(self.request, '更新しました')

        try:
            information = float(self.request.POST.get('information'))
            user_id = self.request.user.id
            schedule_id = self.kwargs['pk']

            today = datetime.datetime.now()
            year = self.request.POST.get('year')
            month = self.request.POST.get('month')
            day = self.request.POST.get('day')

            start_index = int(self.request.POST.get('start'))
            start_time = Schedule.time_choices[start_index][1]
            schedule_start = year + month + day + start_time
            schedule_start = datetime.datetime.strptime(schedule_start, '%Y%m%d%H:%M')
            start_delta = schedule_start - today

            end_index = int(self.request.POST.get('end'))
            end_time = Schedule.time_choices[end_index][1]
            schedule_end = year + month + day + end_time
            schedule_end = datetime.datetime.strptime(schedule_end, '%Y%m%d%H:%M')
            end_delta = schedule_end - today
            end_delta = end_delta.days * 24 * 60 * 60 + end_delta.seconds

            if end_delta <= 0:
                delta = 2
                information =None
            else:
                delta = (start_delta.days * 24 - information) * 60 * 60 + start_delta.seconds
                if delta <= 0:
                    delta = 2

            try:
                if settings.CELERY_TASK_ALWAYS_EAGER:
                    fake = Faker()
                    Faker.seed(8282)
                    task_id = fake.uuid4()
            except AttributeError:
                task_id = str(uuid.uuid4())

            tasks.sender.apply_async(
                kwargs={'user_id':user_id, 'schedule_id':schedule_id, 'information':information},
                countdown=delta,
                task_id=task_id
            )

            tasks.save_task_id.apply_async(
                kwargs={'task_id':task_id, 'schedule_id':schedule_id},
                countdown=1
            )

        except ValueError:
            pass

        return super().form_valid(form)


class ScheduleDeleteView(UserMatchMixin, DeleteView):
    model = Schedule
    success_url = reverse_lazy('weatherapp:home')
    login_url = reverse_lazy('login')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, '削除しました')

        schedule = Schedule.objects.get(id=self.kwargs['pk'])
        app.control.revoke(schedule.task_id, terminate=True)

        return super().delete(request, *args, **kwargs)
