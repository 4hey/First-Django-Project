from django import forms

from .models import Schedule
from accounts.models import User

import datetime
import time


class ScheduleForm(forms.ModelForm):

    this_year = int(datetime.date.today().strftime('%Y'))

    user = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.HiddenInput())
    year = forms.IntegerField(widget=forms.HiddenInput())
    month = forms.IntegerField(widget=forms.HiddenInput())
    day = forms.IntegerField(widget=forms.HiddenInput())

    title = forms.CharField(widget=forms.TextInput(attrs={'size': 50}))
    detail = forms.CharField(widget=forms.Textarea())

    class Meta:
        model = Schedule
        exclude = ('task_id',)
