# File: country_app/urls.py

from django.urls import path
from country_app.views import CountriesView

urlpatterns = [
   path('countries/', CountriesView.as_view(), name='unique-country-list'),
]
