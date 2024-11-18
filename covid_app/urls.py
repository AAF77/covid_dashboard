from django.urls import path
from .views import CovidDataFilteredView

urlpatterns = [
    path('covid/filter/', CovidDataFilteredView.as_view(), name='covid-filtered'),
]
