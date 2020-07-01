from django.contrib import admin
from .models import Schedule, WeatherForecast, ProbabilityOfRain

admin.site.register(Schedule)
admin.site.register(WeatherForecast)
admin.site.register(ProbabilityOfRain)
