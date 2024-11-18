from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from data_app.models import CovidData, VaccinationData
from django.db.models import Sum
from rest_framework.exceptions import ValidationError


# Helper functions for dropdown options
def get_country_choices():
    return sorted(list(CovidData.objects.values_list('country__name', flat=True).distinct()))


def get_region_choices():
    return sorted(list(CovidData.objects.values_list('province_state', flat=True).distinct()))


class GlobalCovidStatisticsView(APIView):
    """
    Provides global summary statistics for COVID-19 data, with optional filtering.
    """
    @swagger_auto_schema(
        operation_description="Retrieve global summary statistics for COVID-19 data, with optional filtering by country or region.",
        manual_parameters=[
            openapi.Parameter(
                'country_name', openapi.IN_QUERY,
                description="Filter by country name",
                type=openapi.TYPE_STRING,
                enum=get_country_choices()  # Dropdown for country names
            ),
            openapi.Parameter(
                'region_name', openapi.IN_QUERY,
                description="Filter by region name (province/state)",
                type=openapi.TYPE_STRING,
                enum=get_region_choices()  # Dropdown for region names
            )
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "total_confirmed": openapi.Schema(type=openapi.TYPE_INTEGER, description="Total confirmed cases"),
                    "total_deaths": openapi.Schema(type=openapi.TYPE_INTEGER, description="Total deaths"),
                    "total_recovered": openapi.Schema(type=openapi.TYPE_INTEGER, description="Total recovered cases"),
                    "total_active": openapi.Schema(type=openapi.TYPE_INTEGER, description="Total active cases"),
                }
            ),
            400: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "error": openapi.Schema(type=openapi.TYPE_STRING, description="Error message")
                }
            )
        }
    )
    def get(self, request):
        country_name = request.query_params.get('country_name', None)
        region_name = request.query_params.get('region_name', None)

        # Validate dropdown values
        country_choices = get_country_choices()
        region_choices = get_region_choices()

        if country_name and country_name not in country_choices:
            raise ValidationError({"error": f"Invalid country_name. Available choices: {', '.join(country_choices)}"})

        if region_name and region_name not in region_choices:
            raise ValidationError({"error": f"Invalid region_name. Available choices: {', '.join(region_choices)}"})

        # Initial queryset
        queryset = CovidData.objects.all()

        # Filter by country name
        if country_name:
            queryset = queryset.filter(country__name__exact=country_name)

        # Filter by region name
        if region_name:
            queryset = queryset.filter(province_state__exact=region_name)

        # Check if no records are found
        if not queryset.exists():
            return Response({"error": "No data found for the given filters."}, status=404)

        # Aggregate data
        total_confirmed = queryset.aggregate(Sum('confirmed'))['confirmed__sum'] or 0
        total_deaths = queryset.aggregate(Sum('deaths'))['deaths__sum'] or 0
        total_recovered = queryset.aggregate(Sum('recovered'))['recovered__sum'] or 0
        total_active = queryset.aggregate(Sum('active'))['active__sum'] or 0

        return Response({
            "total_confirmed": total_confirmed,
            "total_deaths": total_deaths,
            "total_recovered": total_recovered,
            "total_active": total_active
        })


class GlobalVaccinationStatisticsView(APIView):
    """
    Provides global summary statistics for vaccination data, with optional filtering.
    """
    @swagger_auto_schema(
        operation_description="Retrieve global summary statistics for vaccination data, with optional filtering by country.",
        manual_parameters=[
            openapi.Parameter(
                'country_name', openapi.IN_QUERY,
                description="Filter by country name",
                type=openapi.TYPE_STRING,
                enum=get_country_choices()  # Dropdown for country names
            )
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "total_vaccinations": openapi.Schema(type=openapi.TYPE_INTEGER, description="Total vaccinations administered"),
                    "persons_first_dose": openapi.Schema(type=openapi.TYPE_INTEGER, description="Total people vaccinated with the first dose"),
                    "persons_last_dose": openapi.Schema(type=openapi.TYPE_INTEGER, description="Total people vaccinated with the last dose"),
                    "persons_booster_doses": openapi.Schema(type=openapi.TYPE_INTEGER, description="Total booster doses administered"),
                }
            ),
            400: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "error": openapi.Schema(type=openapi.TYPE_STRING, description="Error message")
                }
            )
        }
    )
    def get(self, request):
        country_name = request.query_params.get('country_name', None)

        # Validate dropdown values
        country_choices = get_country_choices()

        if country_name and country_name not in country_choices:
            raise ValidationError({"error": f"Invalid country_name. Available choices: {', '.join(country_choices)}"})

        # Initial queryset
        queryset = VaccinationData.objects.all()

        # Filter by country name
        if country_name:
            queryset = queryset.filter(country__name__exact=country_name)

        # Check if no records are found
        if not queryset.exists():
            return Response({"error": "No data found for the given filters."}, status=404)

        # Aggregate data
        total_vaccinations = queryset.aggregate(Sum('total_vaccinations'))['total_vaccinations__sum'] or 0
        persons_first_dose = queryset.aggregate(Sum('persons_vaccinated_first_dose'))['persons_vaccinated_first_dose__sum'] or 0
        persons_last_dose = queryset.aggregate(Sum('persons_last_dose'))['persons_last_dose__sum'] or 0
        persons_booster_doses = queryset.aggregate(Sum('persons_booster_add_dose'))['persons_booster_add_dose__sum'] or 0

        return Response({
            "total_vaccinations": total_vaccinations,
            "persons_first_dose": persons_first_dose,
            "persons_last_dose": persons_last_dose,
            "persons_booster_doses": persons_booster_doses
        })
