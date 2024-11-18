from django.db import models

class CovidStaticData(models.Model):
    country_name = models.CharField(max_length=255)
    state = models.CharField(max_length=255, null=True, blank=True)
    year = models.IntegerField(default=2021)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    total_deaths = models.BigIntegerField(default=0)
    total_active = models.BigIntegerField(default=0)
    total_confirmed = models.BigIntegerField(default=0)
    total_recovered = models.BigIntegerField(default=0)

    class Meta:
        unique_together = ('country_name', 'state', 'year')

    def __str__(self):
        return f"{self.country_name} - {self.state or 'All'} ({self.year})"
