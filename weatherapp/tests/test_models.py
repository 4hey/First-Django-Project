from django.test import TestCase
from django.db import models
from django.db.models import ForeignKey
from weatherapp.models import Schedule, WeatherForecast, ProbabilityOfRain
from accounts.models import User


class ScheduleModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Schedule.objects.create(
            year=2020,
            month=4,
            day=2,
            title='django practice',
            detail='Study about TestCase in Django',
            start='0',
            end='1',
            place='in',
            user=User.objects.create(username='someone', prefecture=10, city=33),
        )


    def setUp(self):
        self.schedule = Schedule.objects.get(id=1)


    def test_year_label(self):
        field_label = self.schedule._meta.get_field('year').verbose_name
        self.assertEqual(field_label, 'year')

    def test_month_label(self):
        field_label = self.schedule._meta.get_field('month').verbose_name
        self.assertEqual(field_label, 'month')

    def test_day_label(self):
        field_label = self.schedule._meta.get_field('day').verbose_name
        self.assertEqual(field_label, 'day')

    def test_title_label(self):
        field_label = self.schedule._meta.get_field('title').verbose_name
        self.assertEqual(field_label, 'title')

    def test_detail_label(self):
        field_label = self.schedule._meta.get_field('detail').verbose_name
        self.assertEqual(field_label, 'detail')

    def test_start_label(self):
        field_label = self.schedule._meta.get_field('start').verbose_name
        self.assertEqual(field_label, 'start')

    def test_end_label(self):
        field_label = self.schedule._meta.get_field('end').verbose_name
        self.assertEqual(field_label, 'end')

    def test_information_label(self):
        field_label = self.schedule._meta.get_field('information').verbose_name
        self.assertEqual(field.label, 'information')

    def test_user_label(self):
        field_label = self.schedule._meta.get_field('user').verbose_name
        self.assertEqual(field_label, 'user')

    def test_task_id_label(self):
        field_label = self.schedule._meta.get_field('task_id').verbose_name
        self.assertEqual(field_name, 'task_id')

    def test_title_max_length(self):
        max_length = self.schedule._meta.get_field('title').max_length
        self.assertEqual(max_length, 50)

    def test_detail_max_length(self):
        max_length = self.schedule._meta.get_field('detail').max_length
        self.assertEqual(max_length, 200)

    def test_start_max_length(self):
        max_length = self.schedule._meta.get_field('start').max_length
        self.assertEqual(max_length, 2)

    def test_end_max_length(self):
        max_length = self.schedule._meta.get_field('end').max_length
        self.assertEqual(max_length, 2)

    def test_information_max_length(self):
        max_length = self.schedule._meta.get_field('information').max_length
        self.assertEqual(max_length, 3)

    def test_task_id_max_length(self):
        max_length = self.schedule._meta.get_field('task_id').max_length
        self.assertEqual(max_length, 36)

    def test_start_default(self):
        default = self.schedule._meta.get_field('start').default
        self.assertEqual(default, '0')

    def test_end_default(self):
        default = self.schedule._meta.get_field('end').default
        self.assertEqual(default, '1')

    def test_place_default(self):
        default = self.schedule._meta.get_field('place').default
        self.assertEqual(default, 'in')

    def test_start_choices(self):
        time_choices = []
        num = (i for i in range(48))
        for a in range(24):
            time_choices.append((str(next(num)), str(a)+":00"))
            time_choices.append((str(next(num)), str(a)+":30"))
        choices = self.schedule._meta.get_field('start').choices
        self.assertEqual(choices, time_choices)

    def test_end_choices(self):
        time_choices = []
        num = (i for i in range(48))
        for a in range(24):
            time_choices.append((str(next(num)), str(a)+":00"))
            time_choices.append((str(next(num)), str(a)+":30"))
        choices = self.schedule._meta.get_field('end').choices
        self.assertEqual(choices, time_choices)

    def test_information_choices(self):
        information_choices = [
            ('0.5', '30分前'), ('1', '1時間前'), ('2', '2時間前'), ('3', '3時間前'),
            ('6', '6時間前'), ('12', '12時間前'), ('24', '24時間前')
        ]
        choices = self.schedule._meta.get_field('place').choices
        self.assertEqual(choices, information_choices)

    def test_object_name_is_title(self):
        expected_object_name = self.schedule.title
        self.assertEqual(expected_object_name, str(self.schedule))


class WeatherForecastModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        WeatherForecast.objects.create(
            prefecture = '東京',
            city = '東京',
            how_many_days_latter = 0,
            weather = '晴れ'
        )

    def setUp(self):
        self.weather_forecast = WeatherForecast.objects.get(id=1)

    def test_prefecture_label(self):
        field_label = self.weather_forecast._meta.get_field('prefecture').verbose_name
        self.assertEqual(field_label, 'prefecture')

    def test_city_label(self):
        field_label = self.weather_forecast._meta.get_field('city').verbose_name
        self.assertEqual(field_label, 'city')

    def test_how_many_days_latter_label(self):
        field_label = self.weather_forecast._meta.get_field('how_many_days_latter').verbose_name
        self.assertEqual(field_label, 'how many days latter')

    def test_weather_label(self):
        field_label = self.weather_forecast._meta.get_field('weather').verbose_name
        self.assertEqual(field_label, 'weather')

    def test_prefecture_max_length(self):
        max_length = self.weather_forecast._meta.get_field('prefecture').max_length
        self.assertEqual(max_length, 3)

    def test_city_max_length(self):
        max_length = self.weather_forecast._meta.get_field('city').max_length
        self.assertEqual(max_length, 4)

    def test_weather_max_length(self):
        max_length = self.weather_forecast._meta.get_field('weather').max_length
        self.assertEqual(max_length, 5)

    def test_object_name_is_city_and_how_many_days_latter(self):
        expected_object_name = self.weather_forecast.city + str(self.weather_forecast.how_many_days_latter)
        self.assertEqual(expected_object_name, str(self.weather_forecast))


class ProbabilityOfRainModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        ProbabilityOfRain.objects.create(
            prefecture = '東京',
            city = '東京',
            hour = '0-6',
            prob_rain = '0%',
            day = 0
        )

    def setUp(self):
        self.probability = ProbabilityOfRain.objects.get(id=1)

    def test_prefecture_label(self):
        field_label = self.probability._meta.get_field('prefecture').verbose_name
        self.assertEqual(field_label, 'prefecture')

    def test_city_label(self):
        field_label = self.probability._meta.get_field('city').verbose_name
        self.assertEqual(field_label, 'city')

    def test_hour_label(self):
        field_label = self.probability._meta.get_field('hour').verbose_name
        self.assertEqual(field_label, 'hour')

    def test_prob_rain_label(self):
        field_label = self.probability._meta.get_field('prob_rain').verbose_name
        self.assertEqual(field_label, 'prob rain')

    def test_day_label(self):
        field_label = self.probability._meta.get_field('day').verbose_name
        self.assertEqual(field_label, 'day')

    def test_prefecture_max_length(self):
        field_label = self.probability._meta.get_field('prefecture').max_length
        self.assertEqual(field_label, 3)

    def test_city_max_length(self):
        field_label = self.probability._meta.get_field('city').max_length
        self.assertEqual(field_label, 4)

    def test_hour_max_length(self):
        field_label = self.probability._meta.get_field('hour').max_length
        self.assertEqual(field_label, 5)

    def test_prob_rain_max_length(self):
        field_label = self.probability._meta.get_field('prob_rain').max_length
        self.assertEqual(field_label, 3)

    def test_object_name_is_city_and_day_and_hour(self):
        expected_object_name = self.probability.city + str(self.probability.day) + '(' + self.probability.hour + ')'
