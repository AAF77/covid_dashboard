# File: country_app/urls.py

from django.urls import path
from country_app.views import CountrySearchView

urlpatterns = [
   path('countries/', CountrySearchView.as_view(), name='unique-country-list'),
]
