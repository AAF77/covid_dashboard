from django.contrib import admin
from .models import Country, CovidData, VaccinationData

admin.site.register(Country)
admin.site.register(CovidData)
admin.site.register(VaccinationData)
