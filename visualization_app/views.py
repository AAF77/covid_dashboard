from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.exceptions import ValidationError
from visualization_app.models import CovidStaticData
from data_app.models import VaccinationData


# Helper functions to generate dropdown options
def get_country_choices():
    return sorted(list(CovidStaticData.objects.values_list('country_name', flat=True).distinct()))


def get_state_choices():
    return sorted(list(CovidStaticData.objects.values_list('state', flat=True).distinct()))


class VaccinationDataAggregationView(APIView):
    """
    Provides aggregated vaccination data by country and state.
    Avoid repeated records for the same country or state.
    """

    @swagger_auto_schema(
        operation_description="Retrieve aggregated vaccination data for each country and state. Avoid repeated data.",
        manual_parameters=[
            openapi.Parameter(
                'country_name', openapi.IN_QUERY,
                description="Filter by country name",
                type=openapi.TYPE_STRING,
                enum=get_country_choices()
            ),
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "country_name": openapi.Schema(type=openapi.TYPE_STRING, description="Name of the country"),
                        "total_vaccinations": openapi.Schema(type=openapi.TYPE_INTEGER, description="Total vaccinations"),
                        "persons_first_dose": openapi.Schema(type=openapi.TYPE_INTEGER, description="Total first dose vaccinations"),
                        "persons_last_dose": openapi.Schema(type=openapi.TYPE_INTEGER, description="Total last dose vaccinations"),
                        "persons_booster_dose": openapi.Schema(type=openapi.TYPE_INTEGER, description="Total booster doses"),
                    }
                )
            ),
            404: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "error": openapi.Schema(type=openapi.TYPE_STRING, description="No data found.")
                }
            )
        }
    )
    def get(self, request):
        country_name = request.query_params.get('country_name', None)

        # Base queryset
        queryset = VaccinationData.objects.all()

        if country_name:
            queryset = queryset.filter(country__name__iexact=country_name)

        if not queryset.exists():
            return Response({"error": "No vaccination data found for the given filters."}, status=404)

        # Use distinct to avoid repeating countries
        unique_data = queryset.order_by('country__name').first()

        # Format the response
        result = [
            {
                "country_name": unique_data.country.name,
                "total_vaccinations": unique_data.total_vaccinations,
                "persons_first_dose": unique_data.persons_vaccinated_first_dose,
                "persons_last_dose": unique_data.persons_last_dose,
                "persons_booster_dose": unique_data.persons_booster_add_dose,
            }
        ]

        return Response(result)


class CovidDataHeatmapView(APIView):
    """
    Provides precomputed COVID-19 data for a heatmap by country and state.
    Filters by year, country, or both.
    """

    @swagger_auto_schema(
        operation_description="Retrieve precomputed COVID-19 data for a heatmap. Filter by year, country, or both.",
        manual_parameters=[
            openapi.Parameter(
                'year', openapi.IN_QUERY,
                description="Filter by specific year (e.g., 2021)",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'country_name', openapi.IN_QUERY,
                description="Filter by specific country",
                type=openapi.TYPE_STRING,
                enum=get_country_choices()
            )
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "country_name": openapi.Schema(type=openapi.TYPE_STRING, description="Name of the country"),
                        "state": openapi.Schema(type=openapi.TYPE_STRING, description="Name of the state/province"),
                        "latitude": openapi.Schema(type=openapi.TYPE_NUMBER, description="Latitude of the region"),
                        "longitude": openapi.Schema(type=openapi.TYPE_NUMBER, description="Longitude of the region"),
                        "total_deaths": openapi.Schema(type=openapi.TYPE_INTEGER, description="Total deaths"),
                        "total_active": openapi.Schema(type=openapi.TYPE_INTEGER, description="Total active cases"),
                        "total_confirmed": openapi.Schema(type=openapi.TYPE_INTEGER, description="Total confirmed cases"),
                        "total_recovered": openapi.Schema(type=openapi.TYPE_INTEGER, description="Total recovered cases"),
                    }
                )
            ),
            404: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "error": openapi.Schema(type=openapi.TYPE_STRING, description="No data found.")
                }
            )
        }
    )
    def get(self, request):
        year = request.query_params.get('year', None)
        country_name = request.query_params.get('country_name', None)

        # Base queryset
        queryset = CovidStaticData.objects.all()

        # Apply filters
        if year:
            try:
                year = int(year)
                queryset = queryset.filter(year=year)
            except ValueError:
                raise ValidationError({"error": "Invalid year. Please provide a valid numeric year."})

        if country_name:
            queryset = queryset.filter(country_name__iexact=country_name)

        # Check for empty results
        if not queryset.exists():
            return Response({"error": "No COVID-19 data found for the given filters."}, status=404)

        # Format the response
        result = [
            {
                "country_name": data.country_name,
                "state": data.state,
                "latitude": data.latitude,
                "longitude": data.longitude,
                "total_deaths": data.total_deaths,
                "total_active": data.total_active,
                "total_confirmed": data.total_confirmed,
                "total_recovered": data.total_recovered,
            }
            for data in queryset
        ]

        return Response(result)
