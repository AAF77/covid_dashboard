from django.urls import path
from .views import (
    GlobalCovidStatisticsView,
    GlobalVaccinationStatisticsView,
)

urlpatterns = [
    path('statistics/covid/global/', GlobalCovidStatisticsView.as_view(), name='global-covid-statistics'),
    path('statistics/vaccination/global/', GlobalVaccinationStatisticsView.as_view(), name='global-vaccination-statistics'),
]
