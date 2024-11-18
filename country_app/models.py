# File: country_app/models.py

from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Unique country name
    latitude = models.FloatField(null=True, blank=True)  # Optional latitude
    longitude = models.FloatField(null=True, blank=True)  # Optional longitude

    def __str__(self):
        return self.name
