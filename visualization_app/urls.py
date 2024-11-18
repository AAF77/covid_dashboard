from django.urls import path
from .views import VaccinationDataAggregationView, CovidDataHeatmapView

urlpatterns = [
    path('vaccination-data/', VaccinationDataAggregationView.as_view(), name='vaccination-data'),
    path('covid-heatmap/', CovidDataHeatmapView.as_view(), name='covid-heatmap'),
]
