from django.db import models

class ForecastMetadata(models.Model):
    forecast_type = models.CharField(max_length=255)  # e.g., 'ARIMA', 'Linear Regression'
    target_variable = models.CharField(max_length=255)  # e.g., 'confirmed cases'
    country_name = models.CharField(max_length=255, null=True, blank=True)  # If forecast is country-specific
    state = models.CharField(max_length=255, null=True, blank=True)  # If forecast is state-specific
    generated_on = models.DateTimeField(auto_now_add=True)
    forecast_csv_path = models.CharField(max_length=255)  # Path to the CSV file containing forecast results

    def __str__(self):
        return f"{self.forecast_type} forecast for {self.target_variable} ({self.country_name or 'Global'})"
