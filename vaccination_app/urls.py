from django.urls import path
from .views import (
    VaccinationDataFilteredView,
)

urlpatterns = [
    path('vaccinations/filter/', VaccinationDataFilteredView.as_view(), name='vaccination-filtered'),
]
