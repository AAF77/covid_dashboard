from django.urls import path
from .views import CountryForecastView

urlpatterns = [
    path('country-forecast/', CountryForecastView.as_view(), name='country-forecast'),
]
