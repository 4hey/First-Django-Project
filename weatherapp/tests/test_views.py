from django.test import TestCase, override_settings
from django.test.client import Client
from django.urls import reverse
from django.core import mail
from accounts.models import User
from weatherapp.models import Schedule, WeatherForecast, ProbabilityOfRain
from django.template.loader import render_to_string
#from django.utils.translation import gettext_lazy
import datetime
import calendar
from dateutil.relativedelta import relativedelta
from faker import Faker
from weather import tasks
from unittest import mock

from weather import settings


class ScheduleListViewTest(TestCase):
    def setUp(self):
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

        client = Client()

        self.user1 = User.objects.create_user(
            username='tester',
            password='test',
            prefecture=27, #大阪
            city=76 #大阪
        )

        self.user2 = User.objects.create_user(
            username='tester2',
            password='test2',
            prefecture=23, #三重
            city=68 #津
        )

        Schedule.objects.create(
            year=2020,
            month=4,
            day=2,
            title='django practice',
            detail='Study about TestCase in Django',
            start='0',
            end='1',
            information='0.5',
            user=self.user1
        )

        Schedule.objects.create(
            year=2020,
            month=5,
            day=3,
            title='django practice2',
            detail='Study about TestCase in Django2',
            start='0',
            end='1',
            information='0.5',
            user=self.user2
        )

        Schedule.objects.create(
            year=2020,
            month=4,
            day=3,
            title='django practice3',
            detail='Study about TestCase in Django3',
            start='0',
            end='1',
            information='0.5',
            user=self.user1
        )

        for i in range(8):
            WeatherForecast.objects.create(
                prefecture='東京',
                city='東京',
                how_many_days_latter=i,
                weather='東京の天気'+ str(i)
            )

        for i in range(8):
            WeatherForecast.objects.create(
                prefecture='大阪',
                city='大阪',
                how_many_days_latter=i,
                weather='大阪の天気'+ str(i)
            )

    def test_view_url_exists_an_desired_location(self):
        response = self.client.get('/weatherapp/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weatherapp/home.html')

        ca = calendar.Calendar(firstweekday=0)
        week_list = ca.monthdayscalendar(self.current_year, self.current_month)

        weather_list = WeatherForecast.objects.filter(prefecture='東京', city='東京')
        weather = []
        for i in weather_list:
            weather.append(i.weather)

        self.assertEqual(response.context['prefecture'], '東京')
        self.assertEqual(response.context['city'], '東京')
        self.assertEqual(response.context['week_list'], week_list)
        self.assertEqual(response.context['weather'], weather)
        self.assertEqual(response.context['todays_weather'], weather[0])
        self.assertEqual(response.context['days'], self.days)
        self.assertEqual(response.context['weekdays'], self.weekdays)
        self.assertEqual(response.context['current_year'], self.current_year)
        self.assertEqual(response.context['current_month'], self.current_month)
        self.assertEqual(response.context['current_day'], self.current_day)
        self.assertEqual(response.context['indicative_year'], self.current_year)
        self.assertEqual(response.context['indicative_month'], self.current_month)
        self.assertEqual(response.context['indicative_day'], self.current_day)
        self.assertEqual(response.context['month_schedule'], None)

    def test_view_name_exists_an_desired_location(self):
        response = self.client.get(reverse('weatherapp:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weatherapp/home.html')

    def test_name_logged_in_uses_correct_template(self):
        self.client.login(username='tester', password='test') #user1でログイン
        response = self.client.get(reverse('weatherapp:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weatherapp/home.html')

        ca = calendar.Calendar(firstweekday=0)
        week_list = ca.monthdayscalendar(self.current_year, self.current_month)

        weather_list = WeatherForecast.objects.filter(
            prefecture=self.user1.get_prefecture_display(),
            city=self.user1.get_city_display()
        )
        weather = []
        for i in weather_list:
            weather.append(i.weather)

        schedule = Schedule.objects.filter(
            year=self.current_year,
            month=self.current_month,
            user=self.user1
        )

        self.assertEqual(response.context['prefecture'], self.user1.get_prefecture_display())
        self.assertEqual(response.context['city'], self.user1.get_city_display())
        self.assertEqual(response.context['week_list'], week_list)
        self.assertEqual(response.context['weather'], weather)
        self.assertEqual(response.context['todays_weather'], weather[0])
        self.assertEqual(response.context['days'], self.days)
        self.assertEqual(response.context['weekdays'], self.weekdays)
        self.assertEqual(response.context['current_year'], self.current_year)
        self.assertEqual(response.context['current_month'], self.current_month)
        self.assertEqual(response.context['current_day'], self.current_day)
        self.assertEqual(response.context['indicative_year'], self.current_year)
        self.assertEqual(response.context['indicative_month'], self.current_month)
        self.assertEqual(response.context['indicative_day'], self.current_day)
        self.assertQuerysetEqual(response.context['month_schedule'], [repr(s) for s in schedule], ordered=False)

        #year, month, day, pre, postがあるとき
    def test_view_url_exists_an_desired_location2(self):
        self.client.login(username='tester', password='test')
        response = self.client.get(reverse('weatherapp:home'), {'pre':5, 'year':2020})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weatherapp/home.html')

        td_month = relativedelta(months=1)
        year_month = datetime.datetime.strptime('2020'+'/'+'5', '%Y/%m')
        indicative_year = int(datetime.datetime.strftime(year_month-td_month, '%Y'))
        indicative_month = int(datetime.datetime.strftime(year_month-td_month, '%m'))
        indicative_day = 1

        ca = calendar.Calendar(firstweekday=0)
        week_list = ca.monthdayscalendar(indicative_year, indicative_month)

        weather_list = WeatherForecast.objects.filter(
            prefecture=self.user1.get_prefecture_display(),
            city=self.user1.get_city_display()
        )
        weather = []
        for i in weather_list:
            weather.append(i.weather)

        schedule = Schedule.objects.filter(
            year=indicative_year,
            month=indicative_month,
            user=self.user1
        )

        self.assertEqual(response.context['prefecture'], self.user1.get_prefecture_display())
        self.assertEqual(response.context['city'], self.user1.get_city_display())
        self.assertEqual(response.context['week_list'], week_list)
        self.assertEqual(response.context['weather'], weather)
        self.assertEqual(response.context['todays_weather'], weather[0])
        self.assertEqual(response.context['days'], self.days)
        self.assertEqual(response.context['weekdays'], self.weekdays)
        self.assertEqual(response.context['current_year'], self.current_year)
        self.assertEqual(response.context['current_month'], self.current_month)
        self.assertEqual(response.context['current_day'], self.current_day)
        self.assertEqual(response.context['indicative_year'], indicative_year)
        self.assertEqual(response.context['indicative_month'], indicative_month)
        self.assertEqual(response.context['indicative_day'], indicative_day)
        self.assertQuerysetEqual(response.context['month_schedule'], [repr(s) for s in schedule], ordered=False)

    def test_view_url_exists_an_desired_location3(self):
        self.client.login(username='tester', password='test')
        response = self.client.get(reverse('weatherapp:home'), {'post':3, 'year':2020})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weatherapp/home.html')

        td_month = relativedelta(months=1)
        year_month = datetime.datetime.strptime('2020'+'/'+'3', '%Y/%m')
        indicative_year = int(datetime.datetime.strftime(year_month+td_month, '%Y'))
        indicative_month = int(datetime.datetime.strftime(year_month+td_month, '%m'))
        indicative_day = 1

        ca = calendar.Calendar(firstweekday=0)
        week_list = ca.monthdayscalendar(indicative_year, indicative_month)

        weather_list = WeatherForecast.objects.filter(
            prefecture=self.user1.get_prefecture_display(),
            city=self.user1.get_city_display()
        )
        weather = []
        for i in weather_list:
            weather.append(i.weather)

        schedule = Schedule.objects.filter(
            year=indicative_year,
            month=indicative_month,
            user=self.user1
        )

        self.assertEqual(response.context['prefecture'], self.user1.get_prefecture_display())
        self.assertEqual(response.context['city'], self.user1.get_city_display())
        self.assertEqual(response.context['week_list'], week_list)
        self.assertEqual(response.context['weather'], weather)
        self.assertEqual(response.context['todays_weather'], weather[0])
        self.assertEqual(response.context['days'], self.days)
        self.assertEqual(response.context['weekdays'], self.weekdays)
        self.assertEqual(response.context['current_year'], self.current_year)
        self.assertEqual(response.context['current_month'], self.current_month)
        self.assertEqual(response.context['current_day'], self.current_day)
        self.assertEqual(response.context['indicative_year'], indicative_year)
        self.assertEqual(response.context['indicative_month'], indicative_month)
        self.assertEqual(response.context['indicative_day'], indicative_day)
        self.assertQuerysetEqual(response.context['month_schedule'], [repr(s) for s in schedule], ordered=False)

    def test_view_url_exists_an_desired_location4(self):
        self.client.login(username='tester', password='test')
        response = self.client.get(reverse('weatherapp:home'), {'day':5, 'month':5, 'year':2020})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weatherapp/home.html')

        indicative_year = 2020
        indicative_month = 5
        indicative_day = 5

        ca = calendar.Calendar(firstweekday=0)
        week_list = ca.monthdayscalendar(indicative_year, indicative_month)

        weather_list = WeatherForecast.objects.filter(
            prefecture=self.user1.get_prefecture_display(),
            city=self.user1.get_city_display()
        )
        weather = []
        for i in weather_list:
            weather.append(i.weather)

        schedule = Schedule.objects.filter(
            year=indicative_year,
            month=indicative_month,
            user=self.user1
        )

        self.assertEqual(response.context['prefecture'], self.user1.get_prefecture_display())
        self.assertEqual(response.context['city'], self.user1.get_city_display())
        self.assertEqual(response.context['week_list'], week_list)
        self.assertEqual(response.context['weather'], weather)
        self.assertEqual(response.context['todays_weather'], weather[0])
        self.assertEqual(response.context['days'], self.days)
        self.assertEqual(response.context['weekdays'], self.weekdays)
        self.assertEqual(response.context['current_year'], self.current_year)
        self.assertEqual(response.context['current_month'], self.current_month)
        self.assertEqual(response.context['current_day'], self.current_day)
        self.assertEqual(response.context['indicative_year'], indicative_year)
        self.assertEqual(response.context['indicative_month'], indicative_month)
        self.assertEqual(response.context['indicative_day'], indicative_day)
        self.assertQuerysetEqual(response.context['month_schedule'], [repr(s) for s in schedule], ordered=False)


class ScheduleCreateViewTest(TestCase):

    def setUp(self):
        client = Client()

        self.user = User.objects.create_user(
            username='tester',
            password='test',
            prefecture=10,
            city=33,
            email='test@gmail.com'
        )

        for i in range(8):
            WeatherForecast.objects.create(
                prefecture='東京',
                city='東京',
                how_many_days_latter=i,
                weather='東京の天気'+ str(i)
            )

        for i in range(8):
            WeatherForecast.objects.create(
                prefecture='大阪',
                city='大阪',
                how_many_days_latter=i,
                weather='大阪の天気'+ str(i)
            )

    def test_url_redirect_if_not_login(self):
        response = self.client.get('/weatherapp/create/', {'year':'2020', 'month':'4', 'day':'6'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/weatherapp/create/%3Fyear%3D2020%26month%3D4%26day%3D6')

    def test_view_name_exists_an_desired_location(self):
        response = self.client.get(reverse('weatherapp:create'), {'year':'2020', 'month':'4', 'day':'6'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/weatherapp/create/%3Fyear%3D2020%26month%3D4%26day%3D6')

    def test_url_logged_in_uses_correct_template(self):
        self.client.login(username='tester', password='test')
        response = self.client.get('/weatherapp/create/', {'year':'2020', 'month':'4', 'day':'6'})
        self.assertContains(response, 'year')
        self.assertContains(response, 'month')
        self.assertContains(response, 'day')
        self.assertContains(response, 'user')
        self.assertContains(response, 'title')
        self.assertContains(response, 'detail')
        self.assertContains(response, 'start')
        self.assertContains(response, 'end')
        self.assertContains(response, 'information')
        self.assertEqual(str(response.context['user']), 'tester')
        self.assertEqual(response.context['form'].initial['year'], 2020)
        self.assertEqual(response.context['form'].initial['month'], 4)
        self.assertEqual(response.context['form'].initial['day'], 6)
        self.assertEqual(response.context['form'].initial['user'], self.user.id)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weatherapp/schedule_form.html')

    def test_name_logged_in_uses_correct_template(self):
        self.client.login(username='tester', password='test')
        response = self.client.get(reverse('weatherapp:create'), {'year':'2020', 'month':'4', 'day':'6'})
        self.assertContains(response, 'year')
        self.assertContains(response, 'month')
        self.assertContains(response, 'day')
        self.assertContains(response, 'user')
        self.assertContains(response, 'title')
        self.assertContains(response, 'detail')
        self.assertContains(response, 'start')
        self.assertContains(response, 'end')
        self.assertContains(response, 'information')
        self.assertEqual(str(response.context['user']), 'tester')
        self.assertEqual(response.context['form'].initial['year'], 2020)
        self.assertEqual(response.context['form'].initial['month'], 4)
        self.assertEqual(response.context['form'].initial['day'], 6)
        self.assertEqual(response.context['form'].initial['user'], self.user.id)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weatherapp/schedule_form.html')

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_post_uses_correct_templates(self):
        self.client.login(username='tester', password='test')
        response = self.client.post(reverse('weatherapp:create'), {
            'year':'2020',
            'month':'4',
            'day':'2',
            'title':'django practice',
            'detail':'Study about TestCase in Django',
            'start':'0',
            'end':'1',
            'information':'1',
            'user':self.user.id,
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('weatherapp:home'))

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_post_uses_correct_templates2(self):
        self.client.login(username='tester', password='test')
        response = self.client.post(reverse('weatherapp:create'), {
            'year':'2020',
            'month':'4',
            'day':'2',
            'title':'django practice',
            'detail':'Study about TestCase in Django',
            'start':'0',
            'end':'1',
            'information':'1',
            'user':self.user.id,
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain[0][0], '/weatherapp/')
        messages = list(response.context['messages'])
        self.assertEqual(str(messages[0]), '保存しました')



    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_sender_if_register_schedule_with_not_passed_information_time(self):

        day = datetime.datetime.today() + datetime.timedelta(hours=3)
        for time_choice in Schedule.time_choices:
            if day.hour == int(time_choice[1].split(':')[0]):
                start = time_choice[0]
                break

        with mock.patch('weather.tasks.sender.apply_async') as sender_mock:
            self.client.login(username='tester', password='test')
            response = self.client.post(reverse('weatherapp:create'), {
                'year':str(day.year),
                'month':str(day.month),
                'day':str(day.day),
                'title':'django practice',
                'detail':'Study about TestCase in Django',
                'start':start,
                'end':'47',
                'information':'1',
                'user':self.user.id,
            })

            today = datetime.datetime.now()
            start_time = Schedule.time_choices[int(start)][1]
            schedule_start = datetime.datetime(day.year, day.month, day.day, day.hour, 0, 0, 0)
            start_delta = schedule_start - today
            delta = (start_delta.days * 24 - 1) * 60 * 60 + start_delta.seconds

            self.assertTrue(sender_mock.called)
            self.assertEqual(sender_mock.call_count, 1)
            fake = Faker()
            Faker.seed(8282)
            task_id = fake.uuid4()
            sender_mock.assert_called_with(
                kwargs={'user_id':self.user.id, 'schedule_id':None, 'information':1.0},
                countdown=delta,
                task_id=task_id
            )

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_sender_if_register_schedule_with_passed_information_time(self):

        day = datetime.datetime.today() + datetime.timedelta(hours=1)
        for time_choice in Schedule.time_choices:
            if day.hour == int(time_choice[1].split(':')[0]):
                start = time_choice[0]

        with mock.patch('weather.tasks.sender.apply_async') as sender_mock:
            self.client.login(username='tester', password='test')
            response = self.client.post(reverse('weatherapp:create'), {
                'year':str(day.year),
                'month':str(day.month),
                'day':str(day.day),
                'title':'django practice',
                'detail':'Study about TestCase in Django',
                'start':start,
                'end':'47',
                'information':'1',
                'user':self.user.id,
            })
            self.assertTrue(sender_mock.called)
            self.assertEqual(sender_mock.call_count, 1)
            fake = Faker()
            Faker.seed(8282)
            task_id = fake.uuid4()
            sender_mock.assert_called_with(
                kwargs={'user_id':self.user.id, 'schedule_id':None, 'information':1},
                countdown=2,
                task_id=task_id
            )

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_sender_if_register_past_schedule(self):
        with mock.patch('weather.tasks.sender.apply_async') as sender_mock:
            self.client.login(username='tester', password='test')
            response = self.client.post(reverse('weatherapp:create'), {
                'year':'2020',
                'month':'4',
                'day':'2',
                'title':'django practice',
                'detail':'Study about TestCase in Django',
                'start':'0',
                'end':'1',
                'information':'1',
                'user':self.user.id,
            })
            self.assertTrue(sender_mock.called)
            self.assertEqual(sender_mock.call_count, 1)
            fake = Faker()
            Faker.seed(8282)
            task_id = fake.uuid4()
            sender_mock.assert_called_with(
                kwargs={'user_id':self.user.id, 'schedule_id':None, 'information':None},
                countdown=2,
                task_id=task_id
            )

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_sender_if_register_tomorrow_schedule(self):

        tomorrow = datetime.datetime.today() + datetime.timedelta(1)

        with mock.patch('weather.tasks.sender.apply_async') as sender_mock:
            self.client.login(username='tester', password='test')
            response = self.client.post(reverse('weatherapp:create'), {
                'year':str(tomorrow.year),
                'month':str(tomorrow.month),
                'day':str(tomorrow.day),
                'title':'django practice',
                'detail':'Study about TestCase in Django',
                'start':'0',
                'end':'1',
                'information':'24',
                'user':self.user.id,
            })
            self.assertTrue(sender_mock.called)
            self.assertEqual(sender_mock.call_count, 1)
            fake = Faker()
            Faker.seed(8282)
            task_id = fake.uuid4()
            sender_mock.assert_called_with(
                kwargs={'user_id':self.user.id, 'schedule_id':None, 'information':24},
                countdown=2,
                task_id=task_id
            )

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_sender_if_other_schedules_exist(self):

        Schedule.objects.create(
            year=2020,
            month=4,
            day=4,
            title='test',
            detail='test',
            start='0',
            end='47',
            information='1',
            user=self.user
        )

        with mock.patch('weather.tasks.sender.apply_async') as sender_mock:
            self.client.login(username='tester', password='test')
            response = self.client.post(reverse('weatherapp:create'), {
                'year':'2020',
                'month':'4',
                'day':'2',
                'title':'django practice',
                'detail':'Study about TestCase in Django',
                'start':'0',
                'end':'1',
                'information':'1',
                'user':self.user.id,
            })
            self.assertTrue(sender_mock.called)
            self.assertEqual(sender_mock.call_count, 1)
            fake = Faker()
            Faker.seed(8282)
            task_id = fake.uuid4()
            sender_mock.assert_called_with(
                kwargs={'user_id':self.user.id, 'schedule_id':2, 'information':None},
                countdown=2,
                task_id=task_id
            )

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_save_task_id(self):
        with mock.patch('weather.tasks.save_task_id.apply_async') as save_task_id_mock:
            self.client.login(username='tester', password='test')
            response = self.client.post(reverse('weatherapp:create'), {
                'year':'2020',
                'month':'4',
                'day':'2',
                'title':'django practice',
                'detail':'Study about TestCase in Django',
                'start':'0',
                'end':'1',
                'information':'1',
                'user':self.user.id
            })
            self.assertTrue(save_task_id_mock.called)
            self.assertEqual(save_task_id_mock.call_count, 1)
            fake = Faker()
            Faker.seed(8282)
            task_id = fake.uuid4()
            save_task_id_mock.assert_called_with(
                kwargs={'task_id':task_id, 'schedule_id':None},
                countdown=1
            )

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_send_mail(self):

        today = datetime.datetime.today()

        schedule = Schedule.objects.create(
            year=today.year,
            month=today.month,
            day=today.day,
            title='django practice',
            detail='Study about TestCase in Django',
            start='46', #0:00
            end='47', #23:30
            information='1',
            user=self.user
        )

        for day in range(2):
            for i in ['0-6', '6-12', '12-18', '18-24']:
                ProbabilityOfRain.objects.create(
                    prefecture='東京',
                    city='東京',
                    hour=i,
                    prob_rain='50%' + '(' + str(day) + ')',
                    day=day
                )


        self.assertEqual(len(mail.outbox),0)
        task = tasks.sender.apply_async(
            kwargs={'user_id':self.user.id, 'schedule_id':1, 'information':1.0},
        )

        prob_rains = []
        prob_rain = ProbabilityOfRain.objects.get(
            city=User.c_choices[self.user.city][1],
            hour='18-24',
            day=0
        )
        prob_rains.append(prob_rain)

        context = {'user':self.user, 'schedule':schedule, 'weather':'東京の天気0', 'prob_rains':prob_rains}

        self.assertEqual(task.state, 'SUCCESS')
        self.assertEqual(len(mail.outbox),1)
        self.assertEqual(mail.outbox[-1].subject, '【weatherapp】登路された予定があります')
        self.assertEqual(mail.outbox[-1].body, render_to_string('weatherapp/mail_message.txt', context))
        self.assertEqual(mail.outbox[-1].from_email, 'information@weatherapp')
        self.assertEqual(mail.outbox[-1].to, [self.user.email])

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_send_mail_if_any_schedule_is_not_registered(self):

        today = datetime.datetime.today()

        schedule = Schedule.objects.create(
            year=today.year,
            month=today.month,
            day=today.day,
            title='django practice',
            detail='Study about TestCase in Django',
            start='0', #0:00
            end='47', #23:30
            information='1',
            user=self.user
        )

        for day in range(2):
            for i in ['0-6', '6-12', '12-18', '18-24']:
                ProbabilityOfRain.objects.create(
                    prefecture='東京',
                    city='東京',
                    hour=i,
                    prob_rain='50%' + '(' + str(day) + ')',
                    day=day
                )


        self.assertEqual(len(mail.outbox),0)
        task = tasks.sender.apply_async(
            kwargs={'user_id':self.user.id, 'schedule_id':None, 'information':1.0},
        )

        start_time = 0
        end_time = 23.5
        now =datetime.datetime.now()
        now = (now.hour * 60 * 60 + now.minute * 60 + now.second) / 3600
        if start_time < now:
            start_time = now
        if end_time < now:
            end_time = now

        hour_list = []
        for i in [(0, '0-6'), (6, '6-12'), (12, '12-18'), (18, '18-24')]:
            if i[0] < end_time:
                hour_list.append(i[1])
        for i in [(6, '0-6'), (12, '6-12'), (18, '12-18'), (24, '18-24')]:
            if i[0] <= start_time:
                del hour_list[0]

        prob_rains = []
        for hour in hour_list:
            prob_rain = ProbabilityOfRain.objects.get(
                city=User.c_choices[self.user.city][1],
                hour=hour,
                day=0
            )
            prob_rains.append(prob_rain)

        context = {'user':self.user, 'schedule':schedule, 'weather':'東京の天気0', 'prob_rains':prob_rains}

        self.assertEqual(task.state, 'SUCCESS')
        self.assertEqual(len(mail.outbox),1)
        self.assertEqual(mail.outbox[-1].subject, '【weatherapp】登路された予定があります')
        self.assertEqual(mail.outbox[-1].body, render_to_string('weatherapp/mail_message.txt', context))
        self.assertEqual(mail.outbox[-1].from_email, 'information@weatherapp')
        self.assertEqual(mail.outbox[-1].to, [self.user.email])

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_send_mail_if_register_past_schedule(self):

        yesterday = datetime.datetime.today() - datetime.timedelta(days=1)

        schedule = Schedule.objects.create(
            year=yesterday.year,
            month=yesterday.month,
            day=yesterday.day,
            title='django practice',
            detail='Study about TestCase in Django',
            start='0', #0:00
            end='47', #23:30
            information='1',
            user=self.user
        )

        for day in range(2):
            for i in ['0-6', '6-12', '12-18', '18-24']:
                ProbabilityOfRain.objects.create(
                    prefecture='東京',
                    city='東京',
                    hour=i,
                    prob_rain='50%' + '(' + str(day) + ')',
                    day=day
                )


        self.assertEqual(len(mail.outbox),0)
        task = tasks.sender.apply_async(
            kwargs={'user_id':self.user.id, 'schedule_id':1, 'information':None},
        )

        context = {'user':self.user, 'schedule':schedule, 'weather':None, 'prob_rains':None}

        self.assertEqual(task.state, 'SUCCESS')
        self.assertEqual(len(mail.outbox),1)
        self.assertEqual(mail.outbox[-1].subject, '【weatherapp】登路された予定があります')
        self.assertEqual(mail.outbox[-1].body, render_to_string('weatherapp/mail_message.txt', context))
        self.assertEqual(mail.outbox[-1].from_email, 'information@weatherapp')
        self.assertEqual(mail.outbox[-1].to, [self.user.email])

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_send_mail_if_register_tomorrow_schedule(self):

        tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)

        schedule = Schedule.objects.create(
            year=tomorrow.year,
            month=tomorrow.month,
            day=tomorrow.day,
            title='django practice',
            detail='Study about TestCase in Django',
            start='0', #0:00
            end='47', #23:30
            information='24',
            user=self.user
        )

        for day in range(2):
            for i in ['0-6', '6-12', '12-18', '18-24']:
                ProbabilityOfRain.objects.create(
                    prefecture='東京',
                    city='東京',
                    hour=i,
                    prob_rain='50%' + '(' + str(day) + ')',
                    day=day
                )


        self.assertEqual(len(mail.outbox),0)
        task = tasks.sender.apply_async(
            kwargs={'user_id':self.user.id, 'schedule_id':1, 'information':24.0},
        )

        start_time = 0
        end_time = 23.5
        hour_list = []
        for i in [(0, '0-6'), (6, '6-12'), (12, '12-18'), (18, '18-24')]:
            if i[0] < end_time:
                hour_list.append(i[1])
        for i in [(6, '0-6'), (12, '6-12'), (18, '12-18'), (24, '18-24')]:
            if i[0] <= start_time:
                del hour_list[0]

        prob_rains = []
        for hour in hour_list:
            prob_rain = ProbabilityOfRain.objects.get(
                city=User.c_choices[self.user.city][1],
                hour=hour,
                day=1
            )
            prob_rains.append(prob_rain)

        context = {'user':self.user, 'schedule':schedule, 'weather':'東京の天気1', 'prob_rains':prob_rains}

        self.assertEqual(task.state, 'SUCCESS')
        self.assertEqual(len(mail.outbox),1)
        self.assertEqual(mail.outbox[-1].subject, '【weatherapp】登路された予定があります')
        self.assertEqual(mail.outbox[-1].body, render_to_string('weatherapp/mail_message.txt', context))
        self.assertEqual(mail.outbox[-1].from_email, 'information@weatherapp')
        self.assertEqual(mail.outbox[-1].to, [self.user.email])

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_send_mail_if_register_already_started_schedule(self):

        today = datetime.datetime.today()

        schedule = Schedule.objects.create(
            year=today.year,
            month=today.month,
            day=today.day,
            title='django practice',
            detail='Study about TestCase in Django',
            start='0', #0:00
            end='47', #23:30
            information='1',
            user=self.user
        )

        for day in range(2):
            for i in ['0-6', '6-12', '12-18', '18-24']:
                ProbabilityOfRain.objects.create(
                    prefecture='東京',
                    city='東京',
                    hour=i,
                    prob_rain='50%' + '(' + str(day) + ')',
                    day=day
                )


        self.assertEqual(len(mail.outbox),0)
        task = tasks.sender.apply_async(
            kwargs={'user_id':self.user.id, 'schedule_id':1, 'information':1.0},
        )

        now =datetime.datetime.now()
        now = (now.hour * 60 * 60 + now.minute * 60 + now.second) / 3600
        start_time = now
        end_time = 23.5

        hour_list = []
        for i in [(0, '0-6'), (6, '6-12'), (12, '12-18'), (18, '18-24')]:
            if i[0] < end_time:
                hour_list.append(i[1])
        for i in [(6, '0-6'), (12, '6-12'), (18, '12-18'), (24, '18-24')]:
            if i[0] <= start_time:
                del hour_list[0]

        prob_rains = []
        for hour in hour_list:
            prob_rain = ProbabilityOfRain.objects.get(
                city=User.c_choices[self.user.city][1],
                hour=hour,
                day=0
            )
            prob_rains.append(prob_rain)

        context = {'user':self.user, 'schedule':schedule, 'weather':'東京の天気0', 'prob_rains':prob_rains}

        self.assertEqual(task.state, 'SUCCESS')
        self.assertEqual(len(mail.outbox),1)
        self.assertEqual(mail.outbox[-1].subject, '【weatherapp】登路された予定があります')
        self.assertEqual(mail.outbox[-1].body, render_to_string('weatherapp/mail_message.txt', context))
        self.assertEqual(mail.outbox[-1].from_email, 'information@weatherapp')
        self.assertEqual(mail.outbox[-1].to, [self.user.email])

    def test_form_invalid_fields(self):
        self.client.login(username='tester', password='test')
        response = self.client.post(reverse('weatherapp:create'), {
            'year':'2020',
            'month':'4',
            'day':'2',
            'title':'t'*51,
            'detail':'d'*201,
            'start':'48',
            'end':'48',
            'information':'48',
            'user':self.user.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weatherapp/schedule_form.html')
        self.assertFormError(
            response,
            'form',
            'title',
            'この値は 50 文字以下でなければなりません( 51 文字になっています)。'
        )
        self.assertFormError(
            response,
            'form',
            'detail',
            'この値は 200 文字以下でなければなりません( 201 文字になっています)。'
        )
        self.assertFormError(
            response,
            'form',
            'start',
            '正しく選択してください。 48 は候補にありません。'
        )
        self.assertFormError(
            response,
            'form',
            'end',
            '正しく選択してください。 48 は候補にありません。'
        )
        self.assertFormError(
            response,
            'form',
            'information',
            '正しく選択してください。 48 は候補にありません。'
        )


class ScheduleUpdateViewTest(TestCase):
    def setUp(self):
        client = Client()

        self.user1 = User.objects.create_user(
            username='tester',
            password='test',
            prefecture=10,
            city=33,
            email='test@gmail.com'
        )

        self.user2 = User.objects.create_user(
            username='tester2',
            password='test2',
            prefecture=23, #三重
            city=68 #津
        )

        Schedule.objects.create(
            year=2020,
            month=4,
            day=2,
            title='django practice',
            detail='Study about TestCase in Django',
            start='0',
            end='1',
            information='1',
            user=self.user1
        )

        Schedule.objects.create(
            year=2020,
            month=5,
            day=3,
            title='django practice2',
            detail='Study about TestCase in Django2',
            start='0',
            end='1',
            information='1',
            user=self.user2
        )

        for i in range(8):
            WeatherForecast.objects.create(
                prefecture='東京',
                city='東京',
                how_many_days_latter=i,
                weather='東京の天気'+ str(i)
            )

        for i in range(8):
            WeatherForecast.objects.create(
                prefecture='大阪',
                city='大阪',
                how_many_days_latter=i,
                weather='大阪の天気'+ str(i)
            )

    def test_url_not_login_403(self):
        response = self.client.get('/weatherapp/1/update/')
        self.assertEqual(response.status_code, 403)

    def test_name_not_login_403(self):
        response = self.client.get(reverse('weatherapp:update', kwargs={'pk':1}))
        self.assertEqual(response.status_code, 403)

    def test_url_logged_in_uses_correct_template(self):
        self.client.login(username='tester', password='test')
        response = self.client.get('/weatherapp/1/update/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weatherapp/schedule_form.html')

    def test_name_logged_in_uses_correct_template(self):
        self.client.login(username='tester', password='test')
        response = self.client.get(reverse('weatherapp:update', kwargs={'pk':1}))
        self.assertContains(response, 'year')
        self.assertContains(response, 'month')
        self.assertContains(response, 'day')
        self.assertContains(response, 'user')
        self.assertContains(response, 'title')
        self.assertContains(response, 'detail')
        self.assertContains(response, 'start')
        self.assertContains(response, 'end')
        self.assertContains(response, 'information')
        self.assertEqual(str(response.context['user']), self.user1.username)
        self.assertEqual(response.context['update'], True)
        self.assertEqual(response.context['form'].initial['year'], 2020)
        self.assertEqual(response.context['form'].initial['month'], 4)
        self.assertEqual(response.context['form'].initial['day'], 2)
        self.assertEqual(response.context['form'].initial['user'], self.user1.id)
        self.assertEqual(response.context['form'].initial['title'], 'django practice')
        self.assertEqual(response.context['form'].initial['detail'], 'Study about TestCase in Django')
        self.assertEqual(response.context['form'].initial['start'], '0')
        self.assertEqual(response.context['form'].initial['end'], '1')
        self.assertEqual(response.context['form'].initial['information'], '1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weatherapp/schedule_form.html')

    def test_HTTP404_for_invalid_schedule_if_logged_in(self):
        self.client.login(username='tester', password='test')
        response = self.client.get(reverse('weatherapp:update', kwargs={'pk':5}))
        self.assertEqual(response.status_code, 404)

    def test_logged_in_user_can_not_update_other(self):
        self.client.login(username='tester', password='test')
        response = self.client.get('/weatherapp/2/update/')
        self.assertEqual(response.status_code, 403)

    def test_post_uses_correct_template(self):
        self.client.login(username='tester', password='test')
        response = self.client.post(reverse('weatherapp:update', kwargs={'pk':1}), {
            'year':'2020',
            'month':'4',
            'day':'2',
            'title':'django practice2',
            'detail':'Study about TestCase in Django',
            'start':'0',
            'end':'1',
            'information':'1',
            'user':self.user1.id
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('weatherapp:home'))

    def test_post_uses_correct_template2(self):
        self.client.login(username='tester', password='test')
        response = self.client.post(reverse('weatherapp:update', kwargs={'pk':1}), {
            'year':'2020',
            'month':'4',
            'day':'2',
            'title':'django practice2',
            'detail':'Study about TestCase in Django',
            'start':'0',
            'end':'1',
            'information':'1',
            'user':self.user1.id
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain[0][0], '/weatherapp/')
        messages = list(response.context['messages'])
        self.assertEqual(str(messages[0]), '更新しました')

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_sender_if_register_schedule_with_not_passed_information_time(self):

        day = datetime.datetime.today() + datetime.timedelta(hours=3)
        for time_choice in Schedule.time_choices:
            if day.hour == int(time_choice[1].split(':')[0]):
                start = time_choice[0]
                break

        with mock.patch('weather.tasks.sender.apply_async') as sender_mock:
            self.client.login(username='tester', password='test')
            response = self.client.post(reverse('weatherapp:update', kwargs={'pk':1}), {
                'year':str(day.year),
                'month':str(day.month),
                'day':str(day.day),
                'title':'django practice2',
                'detail':'Study about TestCase in Django',
                'start':start,
                'end':'47',
                'information':'1',
                'user':self.user1.id,
            })

            today = datetime.datetime.now()
            start_time = Schedule.time_choices[int(start)][1]
            schedule_start = datetime.datetime(day.year, day.month, day.day, day.hour, 0, 0, 0)
            start_delta = schedule_start - today
            delta = (start_delta.days * 24 - 1) * 60 * 60 + start_delta.seconds

            self.assertTrue(sender_mock.called)
            self.assertEqual(sender_mock.call_count, 1)
            fake = Faker()
            Faker.seed(8282)
            task_id = fake.uuid4()
            sender_mock.assert_called_with(
                kwargs={'user_id':self.user1.id, 'schedule_id':1, 'information':1.0},
                countdown=delta,
                task_id=task_id
            )

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_sender_if_register_schedule_with_passed_information_time(self):

        day = datetime.datetime.today() + datetime.timedelta(hours=1)
        for time_choice in Schedule.time_choices:
            if day.hour == int(time_choice[1].split(':')[0]):
                start = time_choice[0]

        with mock.patch('weather.tasks.sender.apply_async') as sender_mock:
            self.client.login(username='tester', password='test')
            response = self.client.post(reverse('weatherapp:update', kwargs={'pk':1}), {
                'year':str(day.year),
                'month':str(day.month),
                'day':str(day.day),
                'title':'django practice2',
                'detail':'Study about TestCase in Django',
                'start':start,
                'end':'47',
                'information':'1',
                'user':self.user1.id,
            })
            self.assertTrue(sender_mock.called)
            self.assertEqual(sender_mock.call_count, 1)
            fake = Faker()
            Faker.seed(8282)
            task_id = fake.uuid4()
            sender_mock.assert_called_with(
                kwargs={'user_id':self.user1.id, 'schedule_id':1, 'information':1.0},
                countdown=2,
                task_id=task_id
            )

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_sender_if_register_past_schedule(self):
        with mock.patch('weather.tasks.sender.apply_async') as sender_mock:
            self.client.login(username='tester', password='test')
            response = self.client.post(reverse('weatherapp:update', kwargs={'pk':1}), {
                'year':'2020',
                'month':'4',
                'day':'2',
                'title':'django practice2',
                'detail':'Study about TestCase in Django',
                'start':'0',
                'end':'1',
                'information':'1',
                'user':self.user1.id,
            })
            self.assertTrue(sender_mock.called)
            self.assertEqual(sender_mock.call_count, 1)
            fake = Faker()
            Faker.seed(8282)
            task_id = fake.uuid4()
            sender_mock.assert_called_with(
                kwargs={'user_id':self.user1.id, 'schedule_id':1, 'information':None},
                countdown=2,
                task_id=task_id
            )

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_sender_if_register_tomorrow_schedule(self):

        tomorrow = datetime.datetime.today() + datetime.timedelta(1)

        with mock.patch('weather.tasks.sender.apply_async') as sender_mock:
            self.client.login(username='tester', password='test')
            response = self.client.post(reverse('weatherapp:update', kwargs={'pk':1}), {
                'year':str(tomorrow.year),
                'month':str(tomorrow.month),
                'day':str(tomorrow.day),
                'title':'django practice',
                'detail':'Study about TestCase in Django',
                'start':'0',
                'end':'1',
                'information':'24',
                'user':self.user1.id,
            })
            self.assertTrue(sender_mock.called)
            self.assertEqual(sender_mock.call_count, 1)
            fake = Faker()
            Faker.seed(8282)
            task_id = fake.uuid4()
            sender_mock.assert_called_with(
                kwargs={'user_id':self.user1.id, 'schedule_id':1, 'information':24},
                countdown=2,
                task_id=task_id
            )

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_save_task_id(self):
        with mock.patch('weather.tasks.save_task_id.apply_async') as save_task_id_mock:
            self.client.login(username='tester', password='test')
            response = self.client.post(reverse('weatherapp:update', kwargs={'pk':1}), {
                'year':'2020',
                'month':'4',
                'day':'2',
                'title':'django practice',
                'detail':'Study about TestCase in Django',
                'start':'0',
                'end':'1',
                'information':'1',
                'user':self.user1.id
            })
            self.assertTrue(save_task_id_mock.called)
            self.assertEqual(save_task_id_mock.call_count, 1)
            fake = Faker()
            Faker.seed(8282)
            task_id = fake.uuid4()
            save_task_id_mock.assert_called_with(
                kwargs={'task_id':task_id, 'schedule_id':1},
                countdown=1
            )

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_send_mail(self):

        today = datetime.datetime.today()

        schedule = Schedule.objects.create(
            year=today.year,
            month=today.month,
            day=today.day,
            title='django practice',
            detail='Study about TestCase in Django',
            start='46', #23:00
            end='47', #23:30
            information='1',
            user=self.user1
        )

        for day in range(2):
            for i in ['0-6', '6-12', '12-18', '18-24']:
                ProbabilityOfRain.objects.create(
                    prefecture='東京',
                    city='東京',
                    hour=i,
                    prob_rain='50%' + '(' + str(day) + ')',
                    day=day
                )

        self.assertEqual(len(mail.outbox),0)
        task = tasks.sender.apply_async(
            kwargs={'user_id':self.user1.id, 'schedule_id':3, 'information':1.0},
        )

        prob_rains = []
        prob_rain = ProbabilityOfRain.objects.get(
            city=User.c_choices[self.user1.city][1],
            hour='18-24',
            day=0
        )
        prob_rains.append(prob_rain)

        context = {'user':self.user1, 'schedule':schedule, 'weather':'東京の天気0', 'prob_rains':prob_rains}

        self.assertEqual(task.state, 'SUCCESS')
        self.assertEqual(len(mail.outbox),1)
        self.assertEqual(mail.outbox[-1].subject, '【weatherapp】登路された予定があります')
        self.assertEqual(mail.outbox[-1].body, render_to_string('weatherapp/mail_message.txt', context))
        self.assertEqual(mail.outbox[-1].from_email, 'information@weatherapp')
        self.assertEqual(mail.outbox[-1].to, [self.user1.email])

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_send_mail_if_register_past_schedule(self):

        yesterday = datetime.datetime.today() - datetime.timedelta(days=1)

        schedule = Schedule.objects.create(
            year=yesterday.year,
            month=yesterday.month,
            day=yesterday.day,
            title='django practice',
            detail='Study about TestCase in Django',
            start='0', #0:00
            end='47', #23:30
            information='1',
            user=self.user1
        )

        for day in range(2):
            for i in ['0-6', '6-12', '12-18', '18-24']:
                ProbabilityOfRain.objects.create(
                    prefecture='東京',
                    city='東京',
                    hour=i,
                    prob_rain='50%' + '(' + str(day) + ')',
                    day=day
                )


        self.assertEqual(len(mail.outbox),0)
        task = tasks.sender.apply_async(
            kwargs={'user_id':self.user1.id, 'schedule_id':3, 'information':None},
        )

        context = {'user':self.user1, 'schedule':schedule, 'weather':None, 'prob_rains':None}

        self.assertEqual(task.state, 'SUCCESS')
        self.assertEqual(len(mail.outbox),1)
        self.assertEqual(mail.outbox[-1].subject, '【weatherapp】登路された予定があります')
        self.assertEqual(mail.outbox[-1].body, render_to_string('weatherapp/mail_message.txt', context))
        self.assertEqual(mail.outbox[-1].from_email, 'information@weatherapp')
        self.assertEqual(mail.outbox[-1].to, [self.user1.email])

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_send_mail_if_register_tomorrow_schedule(self):

        tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)

        schedule = Schedule.objects.create(
            year=tomorrow.year,
            month=tomorrow.month,
            day=tomorrow.day,
            title='django practice',
            detail='Study about TestCase in Django',
            start='0', #0:00
            end='47', #23:30
            information='24',
            user=self.user1
        )

        for day in range(2):
            for i in ['0-6', '6-12', '12-18', '18-24']:
                ProbabilityOfRain.objects.create(
                    prefecture='東京',
                    city='東京',
                    hour=i,
                    prob_rain='50%' + '(' + str(day) + ')',
                    day=day
                )


        self.assertEqual(len(mail.outbox),0)
        task = tasks.sender.apply_async(
            kwargs={'user_id':self.user1.id, 'schedule_id':3, 'information':24.0},
        )

        start_time = 0
        end_time = 23.5
        hour_list = []
        for i in [(0, '0-6'), (6, '6-12'), (12, '12-18'), (18, '18-24')]:
            if i[0] < end_time:
                hour_list.append(i[1])
        for i in [(6, '0-6'), (12, '6-12'), (18, '12-18'), (24, '18-24')]:
            if i[0] <= start_time:
                del hour_list[0]

        prob_rains = []
        for hour in hour_list:
            prob_rain = ProbabilityOfRain.objects.get(
                city=User.c_choices[self.user1.city][1],
                hour=hour,
                day=1
            )
            prob_rains.append(prob_rain)

        context = {'user':self.user1, 'schedule':schedule, 'weather':'東京の天気1', 'prob_rains':prob_rains}

        self.assertEqual(task.state, 'SUCCESS')
        self.assertEqual(len(mail.outbox),1)
        self.assertEqual(mail.outbox[-1].subject, '【weatherapp】登路された予定があります')
        self.assertEqual(mail.outbox[-1].body, render_to_string('weatherapp/mail_message.txt', context))
        self.assertEqual(mail.outbox[-1].from_email, 'information@weatherapp')
        self.assertEqual(mail.outbox[-1].to, [self.user1.email])

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_send_mail_if_register_already_started_schedule(self):

        today = datetime.datetime.today()

        schedule = Schedule.objects.create(
            year=today.year,
            month=today.month,
            day=today.day,
            title='django practice',
            detail='Study about TestCase in Django',
            start='0', #0:00
            end='47', #23:30
            information='1',
            user=self.user1
        )

        for day in range(2):
            for i in ['0-6', '6-12', '12-18', '18-24']:
                ProbabilityOfRain.objects.create(
                    prefecture='東京',
                    city='東京',
                    hour=i,
                    prob_rain='50%' + '(' + str(day) + ')',
                    day=day
                )


        self.assertEqual(len(mail.outbox),0)
        task = tasks.sender.apply_async(
            kwargs={'user_id':self.user1.id, 'schedule_id':3, 'information':1.0},
        )

        now =datetime.datetime.now()
        now = (now.hour * 60 * 60 + now.minute * 60 + now.second) / 3600
        start_time = now
        end_time = 23.5

        hour_list = []
        for i in [(0, '0-6'), (6, '6-12'), (12, '12-18'), (18, '18-24')]:
            if i[0] < end_time:
                hour_list.append(i[1])
        for i in [(6, '0-6'), (12, '6-12'), (18, '12-18'), (24, '18-24')]:
            if i[0] <= start_time:
                del hour_list[0]

        prob_rains = []
        for hour in hour_list:
            prob_rain = ProbabilityOfRain.objects.get(
                city=User.c_choices[self.user1.city][1],
                hour=hour,
                day=0
            )
            prob_rains.append(prob_rain)

        context = {'user':self.user1, 'schedule':schedule, 'weather':'東京の天気0', 'prob_rains':prob_rains}

        self.assertEqual(task.state, 'SUCCESS')
        self.assertEqual(len(mail.outbox),1)
        self.assertEqual(mail.outbox[-1].subject, '【weatherapp】登路された予定があります')
        self.assertEqual(mail.outbox[-1].body, render_to_string('weatherapp/mail_message.txt', context))
        self.assertEqual(mail.outbox[-1].from_email, 'information@weatherapp')
        self.assertEqual(mail.outbox[-1].to, [self.user1.email])



    def test_form_invalid_fields(self):
        self.client.login(username='tester', password='test')
        response = self.client.post(reverse('weatherapp:update', kwargs={'pk':1}), {
            'year':'2020',
            'month':'4',
            'day':'2',
            'title':'t'*51,
            'detail':'d'*201,
            'start':'48',
            'end':'48',
            'information':'1111',
            'user':self.user1.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weatherapp/schedule_form.html')
        self.assertFormError(
            response,
            'form',
            'title',
            'この値は 50 文字以下でなければなりません( 51 文字になっています)。'
        )
        self.assertFormError(
            response,
            'form',
            'detail',
            'この値は 200 文字以下でなければなりません( 201 文字になっています)。'
        )
        self.assertFormError(
            response,
            'form',
            'start',
            '正しく選択してください。 48 は候補にありません。'
        )
        self.assertFormError(
            response,
            'form',
            'end',
            '正しく選択してください。 48 は候補にありません。'
        )
        self.assertFormError(
            response,
            'form',
            'information',
            '正しく選択してください。 1111 は候補にありません。'
        )


class ScheduleDeleteViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username='tester',
            password='test',
            prefecture=10,
            city=33
        )

        user2 = User.objects.create_user(
            username='tester2',
            password='test2',
            prefecture=23, #三重
            city=68 #津
        )

        Schedule.objects.create(
            year=2020,
            month=4,
            day=2,
            title='django practice',
            detail='Study about TestCase in Django',
            start='0',
            end='1',
            information='1',
            user=user
        )

        Schedule.objects.create(
            year=2020,
            month=5,
            day=3,
            title='django practice2',
            detail='Study about TestCase in Django2',
            start='0',
            end='1',
            information='1',
            user=user2
        )

        for i in range(8):
            WeatherForecast.objects.create(
                prefecture='東京',
                city='東京',
                how_many_days_latter=i,
                weather='東京の天気'+ str(i)
            )

        for i in range(8):
            WeatherForecast.objects.create(
                prefecture='大阪',
                city='大阪',
                how_many_days_latter=i,
                weather='大阪の天気'+ str(i)
            )

    def setUp(self):
        client = Client()

    def test_url_not_login_403(self):
        response = self.client.get('/weatherapp/1/delete/')
        self.assertEqual(response.status_code, 403)

    def test_name_not_login_403(self):
        response = self.client.get(reverse('weatherapp:delete', kwargs={'pk':1}))
        self.assertEqual(response.status_code, 403)

    def test_url_logged_in_uses_correct_template(self):
        self.client.login(username='tester', password='test')
        response = self.client.get('/weatherapp/1/delete/')
        self.assertEqual(str(response.context['user']), 'tester')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weatherapp/schedule_confirm_delete.html')

    def test_name_logged_in_uses_correct_template(self):
        self.client.login(username='tester', password='test')
        response = self.client.get(reverse('weatherapp:delete', kwargs={'pk':1}))
        self.assertEqual(str(response.context['user']), 'tester')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weatherapp/schedule_confirm_delete.html')

    def test_HTTP404_for_invalid_schedule_if_logged_in(self):
        self.client.login(username='tester', password='test')
        response = self.client.get(reverse('weatherapp:delete', kwargs={'pk':5}))
        self.assertEqual(response.status_code, 404)

    def test_logged_in_user_can_not_delete_other(self):
        self.client.login(username='tester', password='test')
        response = self.client.get('/weatherapp/2/delete/')
        self.assertEqual(response.status_code, 403)

    def test_post_uses_correct_templates(self):
        self.client.login(username='tester', password='test')
        response = self.client.post(reverse('weatherapp:delete', kwargs={'pk':1}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('weatherapp:home'))
        #削除されたことを確かめる
        response = self.client.get(reverse('weatherapp:delete', kwargs={'pk':1}))
        self.assertEqual(response.status_code, 404)

    def test_post_uses_correct_templates2(self):
        self.client.login(username='tester', password='test')
        response = self.client.post(reverse('weatherapp:delete', kwargs={'pk':1}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain[0][0], '/weatherapp/')
        messages = list(response.context['messages'])
        self.assertEqual(str(messages[0]), '削除しました')
        #削除されたことを確かめる
        response = self.client.get(reverse('weatherapp:delete', kwargs={'pk':1}))
        self.assertEqual(response.status_code, 404)


class CeleryPeriodicTaskTest(TestCase):

    def test_weather_forecast(self):
        task = tasks.weather_forecast.apply()
        self.assertEqual(task.state, 'SUCCESS')
        weathers = WeatherForecast.objects.all()
        self.assertEqual(len(weathers), 1136)
        cities = set()
        prefectures =set()
        for weather in weathers:
            cities.add(weather.city)
            prefectures.add(weather.prefecture)
        self.assertEqual(len(cities), 142)
        self.assertEqual(len(prefectures), 50)
        for city in cities:
            self.assertEqual(len(WeatherForecast.objects.filter(city=city)), 8)

    def test_probability_of_rain(self):
        task = tasks.probability_of_rain.apply()
        self.assertEqual(task.state, 'SUCCESS')
        pofs = ProbabilityOfRain.objects.all()
        self.assertEqual(len(pofs), 1136)
        cities = set()
        prefectures =set()
        for pof in pofs:
            cities.add(pof.city)
            prefectures.add(pof.prefecture)
        self.assertEqual(len(cities), 142)
        self.assertEqual(len(prefectures), 50)
        for city in cities:
            self.assertEqual(len(ProbabilityOfRain.objects.filter(city=city, day=0)), 4)
            self.assertEqual(len(ProbabilityOfRain.objects.filter(city=city, day=1)), 4)
