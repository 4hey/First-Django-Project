from django.test import TestCase
from django import forms
from django.forms import TextInput
from accounts.models import User
from weatherapp.forms import ScheduleForm


class ScheduleFormTest(TestCase):

    def setUp(self) :
        form = ScheduleForm()

        self.user = User.objects.create(username='tester', prefecture=10, city=33)

    def test_user_label(self):
        form = ScheduleForm()
        self.assertTrue(form.fields['user'].label ==  None)

    def test_year_label(self):
        form = ScheduleForm()
        self.assertTrue(form.fields['year'].label ==  None)

    def test_month_label(self):
        form = ScheduleForm()
        self.assertTrue(form.fields['month'].label ==  None)

    def test_day_label(self):
        form = ScheduleForm()
        self.assertTrue(form.fields['day'].label ==  None)

    def test_title_label(self):
        form = ScheduleForm()
        self.assertTrue(form.fields['title'].label ==  None)

    def test_detail_label(self):
        form = ScheduleForm()
        self.assertTrue(form.fields['detail'].label ==  None)

    def test_start_label(self):
        form = ScheduleForm()
        self.assertTrue(form.fields['start'].label ==  'Start')

    def test_end_label(self):
        form = ScheduleForm()
        self.assertTrue(form.fields['end'].label == 'End')

    def test_place_label(self):
        form = ScheduleForm()
        self.assertTrue(form.fields['information'].label ==  'Information')

    def test_title_widget(self):
        form = ScheduleForm()
        self.assertTrue(isinstance(form.fields['title'].widget, TextInput))
        self.assertEqual(form.fields['title'].widget.attrs['size'], 50)

    def test_form_is_valid(self):
        form = ScheduleForm({
            'title':'django practice',
            'detail':'Study about TestCase in Django',
            'start':'0',
            'end':'1',
            'information':'0.5',
            'year':2020,
            'month':4,
            'day':4,
            'user':self.user.id
        })
        self.assertTrue(form.is_valid())

    def test_title_max_length(self):
        title = 'a'*51
        form = ScheduleForm({
            'title':title,
            'detail':'Study about TestCase in Django',
            'start':'0',
            'end':'1',
            'information':'0.5',
            'year':2020,
            'month':4,
            'day':4,
            'user':self.user.id
        })
        self.assertFalse(form.is_valid())

    def test_detail_max_length(self):
        detail = 'a'*201
        form = ScheduleForm({
            'title':'django practice',
            'detail':detail,
            'start':'0',
            'end':'1',
            'information':'0.5',
            'year':2020,
            'month':4,
            'day':4,
            'user':self.user.id
        })
        self.assertFalse(form.is_valid())

    def test_start_max_length(self):
        start = 'a'*3
        form = ScheduleForm({
            'title':'django practice',
            'detail':'Study about TestCase in Django',
            'start':start,
            'end':'1',
            'information':'0.5',
            'year':2020,
            'month':4,
            'day':4,
            'user':self.user.id
        })
        self.assertFalse(form.is_valid())

    def test_end_max_length(self):
        end = 'a'*3
        form = ScheduleForm({
            'title':'django practice',
            'detail':'Study about TestCase in Django',
            'start':'0',
            'end':end,
            'information':'0.5',
            'year':2020,
            'month':4,
            'day':4,
            'user':self.user.id
        })
        self.assertFalse(form.is_valid())

    def test_information_max_length(self):
        place = 'a'*4
        form = ScheduleForm({
            'title':'django practice',
            'detail':'Study about TestCase in Django',
            'start':'0',
            'end':'1',
            'information':'1000',
            'year':2020,
            'month':4,
            'day':4,
            'user':self.user.id
        })
        self.assertFalse(form.is_valid())

    def test_start_initial(self):
        form = ScheduleForm()
        self.assertEqual(form.fields['start'].initial, '0')

    def test_end_initial(self):
        form = ScheduleForm()
        self.assertEqual(form.fields['end'].initial, '1')
