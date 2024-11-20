from django.core.management.base import BaseCommand
from data_app.models import CovidData
from forecasting_app.models import ForecastMetadata
from forecasting_app.utils import generate_forecasts, save_forecasts_to_csv
import pandas as pd

class Command(BaseCommand):
    help = "Precompute forecasts for the next 10 years and save results to CSV."

    def handle(self, *args, **kwargs):
        # Fetch Covid data
        covid_data = CovidData.objects.filter(file_date__isnull=False).values('file_date', 'confirmed')
        data = pd.DataFrame.from_records(covid_data)
        data['file_date'] = pd.to_datetime(data['file_date'])
        data.set_index('file_date', inplace=True)

        if data.empty:
            self.stdout.write(self.style.WARNING("No data available for forecasting."))
            return

        # Generate forecast for the next 10 years starting from 2024
        forecast_results = {}
        try:
            forecast_results = generate_forecasts(data, variable='confirmed', steps=3650)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error during forecast generation: {str(e)}"))
            return

        # Iterate over the forecasted years and save the forecast for each year
        combined_forecast_df = pd.DataFrame()
        for year in range(2024, 2024 + 10):
            # Filtering forecast results for the specific year
            start_date = pd.Timestamp(year=year, month=1, day=1)
            end_date = pd.Timestamp(year=year + 1, month=1, day=1)

            yearly_forecast = forecast_results.loc[
                (forecast_results.index >= start_date) & (forecast_results.index < end_date)
            ]

            # Append the yearly forecast to a combined dataframe
            combined_forecast_df = pd.concat([combined_forecast_df, yearly_forecast])

        # Save the combined forecast to CSV
        csv_path = save_forecasts_to_csv(combined_forecast_df, 'global_confirmed_forecast.csv')

        # Save metadata for the forecast
        ForecastMetadata.objects.create(
            forecast_type="ARIMA",
            target_variable="confirmed cases",
            forecast_csv_path=csv_path
        )

        self.stdout.write(self.style.SUCCESS("Forecast generated and saved successfully."))
