# File: data_app/models.py

from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)  # Optional if necessary
    longitude = models.FloatField(null=True, blank=True)  # Optional if necessary

    def __str__(self):
        return self.name


class VaccinationData(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    total_vaccinations = models.BigIntegerField(default=0)  # Default to 0 if null
    persons_vaccinated_first_dose = models.BigIntegerField(default=0)
    persons_last_dose = models.BigIntegerField(default=0)
    persons_booster_add_dose = models.BigIntegerField(default=0)
    first_vaccine_date = models.DateField(null=True, blank=True)  # Optional if necessary

    def __str__(self):
        return f"{self.country.name} - {self.first_vaccine_date}"


class CovidData(models.Model):
    country = models.ForeignKey('Country', on_delete=models.CASCADE, related_name='covid_data', db_index=True)
    province_state = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    file_date = models.DateField(null=True, blank=True, db_index=True)
    confirmed = models.IntegerField(default=0)
    deaths = models.IntegerField(default=0)
    recovered = models.IntegerField(default=0)
    active = models.IntegerField(default=0)
    incident_rate = models.FloatField(null=True, blank=True)  # Allow float for specific calculations
    case_fatality_ratio = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.country.name} - {self.file_date}"
    
    class Meta:
        indexes = [
            models.Index(fields=['country', 'province_state']),
            models.Index(fields=['file_date']),
        ]
