from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from covid_app.views import get_country_choices
from forecasting_app.models import ForecastMetadata
from data_app.models import CovidData
from forecasting_app.utils import generate_forecasts, save_forecasts_to_csv
import pandas as pd
import os
from rest_framework.pagination import PageNumberPagination

class YearPagination(PageNumberPagination):
    """
    Custom pagination class for year-based pagination.
    """
    page_size = 365  # Assuming one year has 365 days
    page_size_query_param = 'page_size'
    max_page_size = 365  # One year max
    page_query_param = 'year'


class CountryForecastView(APIView):
    """
    API endpoint to generate or retrieve forecasts for deaths, active cases, and recoveries for a specific country.
    Includes pagination for forecasted years.
    """

    @swagger_auto_schema(
        operation_description="Retrieve a year-by-year forecast for deaths, active cases, and recoveries for a specific country.",
        manual_parameters=[
            openapi.Parameter(
                'country_name', openapi.IN_QUERY,
                description="Select a country for the forecast.",
                type=openapi.TYPE_STRING,
                enum=get_country_choices(),  # Dropdown list of countries
            ),
            openapi.Parameter(
                'year', openapi.IN_QUERY,
                description="Page number representing the forecast year (1 for the first year, 2 for the second year, etc.).",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "date": openapi.Schema(type=openapi.TYPE_STRING, description="Forecast date"),
                        "deaths_forecast": openapi.Schema(type=openapi.TYPE_INTEGER, description="Forecasted deaths"),
                        "active_forecast": openapi.Schema(type=openapi.TYPE_INTEGER, description="Forecasted active cases"),
                        "recovered_forecast": openapi.Schema(type=openapi.TYPE_INTEGER, description="Forecasted recoveries"),
                    },
                ),
            ),
            400: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "error": openapi.Schema(type=openapi.TYPE_STRING, description="Error message"),
                },
            ),
        },
    )
    
    def get(self, request, *args, **kwargs):
        country_name = request.query_params.get('country_name', None)
        year = request.query_params.get('year', None)

        if year is None:
            year = 2024  # Default to the first year if not specified
        else:
            year = int(year)

        if not country_name:
            return Response({"error": "country_name parameter is required."}, status=400)

        # Check if a forecast already exists for the country
        existing_forecast = ForecastMetadata.objects.filter(country_name__iexact=country_name).first()

        if existing_forecast:
            csv_path = existing_forecast.forecast_csv_path

            # If the forecast file is missing, regenerate the forecast
            if not os.path.exists(csv_path):
                # Regenerate the forecast if the file is missing
                return self._regenerate_forecast(country_name, year)

            # Load forecast data from the CSV file
            forecast_data = pd.read_csv(csv_path)
            forecast_data['date'] = pd.to_datetime(forecast_data['date'])  # Ensure it's parsed as datetime

            # Construct the start and end dates for the requested year
            start_date = pd.Timestamp(year=year, month=1, day=1)
            end_date = pd.Timestamp(year=year + 1, month=1, day=1)

            # Filter data for the requested year
            paginated_data = forecast_data[
                (forecast_data['date'] >= start_date) & (forecast_data['date'] < end_date)
            ]

            # Format the date column to remove time before returning the response
            paginated_data['date'] = paginated_data['date'].dt.strftime('%Y-%m-%d')

            # Return the paginated response
            return Response(paginated_data.to_dict(orient='records'))

        # If no forecast exists, generate a new one
        return self._regenerate_forecast(country_name, year)


    def _regenerate_forecast(self, country_name, year):
        """
        Regenerates a forecast for the specified country and returns the generated data for the requested year.
        """
        target_variables = ['deaths', 'active', 'recovered']
        covid_data = CovidData.objects.filter(country__name__iexact=country_name, file_date__isnull=False)

        # Convert data to DataFrame
        data = pd.DataFrame.from_records(covid_data.values('file_date', *target_variables))
        if data.empty:
            return Response({"error": f"No data available for the country: {country_name}."}, status=404)

        # Ensure 'file_date' is treated as a datetime object
        data['file_date'] = pd.to_datetime(data['file_date'])
        data.set_index('file_date', inplace=True)

        try:
            # Generate forecasts for the next 10 years
            forecasts = generate_forecasts(data, target_variables, steps=3650)
        except Exception as e:
            return Response({"error": f"Error during forecast generation: {str(e)}"}, status=500)

        # Save the forecasts to a CSV file
        filename_prefix = f"{country_name}"
        csv_path = save_forecasts_to_csv(forecasts, filename_prefix)

        # Save metadata in the database
        ForecastMetadata.objects.create(
            forecast_type="ARIMA",
            target_variable=", ".join(target_variables),
            country_name=country_name,
            forecast_csv_path=csv_path
        )

        # Combine forecast results into a single DataFrame
        combined_df = pd.concat(forecasts.values(), axis=1)

        # Ensure there is a single date column
        if 'date' in combined_df.columns:
            combined_df = combined_df.loc[:, ~combined_df.columns.duplicated()]

        # Convert the date column to datetime if not already in datetime format
        combined_df['date'] = pd.to_datetime(combined_df['date'], errors='coerce')

        # Filter data for the requested year
        # Set start_date with specified year, month, and day to avoid TypeError
        start_date = pd.Timestamp(year=2024, month=1, day=1) + pd.DateOffset(years=(year - 1))
        end_date = start_date + pd.DateOffset(years=1)



        # Make sure the filtering dates are consistent with datetime
        paginated_data = combined_df[
            (combined_df['date'] >= start_date) & (combined_df['date'] < end_date)
        ]

        # Ensure the date column is returned without time
        paginated_data['date'] = paginated_data['date'].dt.strftime('%Y-%m-%d')

        # Return the paginated response
        return Response(paginated_data.to_dict(orient='records'))
