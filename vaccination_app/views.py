from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from data_app.models import VaccinationData
from rest_framework.exceptions import ValidationError
from datetime import datetime


# Helper function to generate dropdown options
def get_country_choices():
    return sorted(list(VaccinationData.objects.values_list('country__name', flat=True).distinct()))


class VaccinationDataFilteredView(APIView):
    """
    Filter vaccination data by country name, date range, or both.
    Display unique records based on `country_name` and `total_vaccinations`.
    """

    @swagger_auto_schema(
        operation_description="Filter vaccination data by country name, date range, or both. Display unique records based on `country_name` and `total_vaccinations`.",
        manual_parameters=[
            openapi.Parameter(
                'country_name', openapi.IN_QUERY,
                description="Name of the country to filter by",
                type=openapi.TYPE_STRING,
                enum=get_country_choices()  # Dropdown for country names
            ),
            openapi.Parameter(
                'start_date', openapi.IN_QUERY,
                description="Start date (YYYY-MM-DD)",
                type=openapi.FORMAT_DATE
            ),
            openapi.Parameter(
                'end_date', openapi.IN_QUERY,
                description="End date (YYYY-MM-DD)",
                type=openapi.FORMAT_DATE
            )
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "count": openapi.Schema(type=openapi.TYPE_INTEGER, description="Total number of records"),
                    "results": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "country_name": openapi.Schema(type=openapi.TYPE_STRING, description="Name of the country"),
                                "total_vaccinations": openapi.Schema(type=openapi.TYPE_INTEGER, description="Total vaccinations"),
                                "persons_vaccinated_first_dose": openapi.Schema(type=openapi.TYPE_INTEGER, description="People vaccinated with the first dose"),
                                "persons_last_dose": openapi.Schema(type=openapi.TYPE_INTEGER, description="People vaccinated with the last dose"),
                                "persons_booster_add_dose": openapi.Schema(type=openapi.TYPE_INTEGER, description="People vaccinated with booster doses"),
                            }
                        )
                    ),
                }
            ),
            400: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "error": openapi.Schema(type=openapi.TYPE_STRING, description="Error message")
                }
            ),
            404: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "error": openapi.Schema(type=openapi.TYPE_STRING, description="No data found")
                }
            ),
        }
    )
    def get(self, request, *args, **kwargs):
        country_name = request.query_params.get('country_name', None)
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)

        # Validate date format
        try:
            if start_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            if end_date:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                if start_date and start_date > end_date:
                    raise ValidationError({"error": "start_date cannot be after end_date."})
        except ValueError:
            raise ValidationError({"error": "Invalid date format. Use YYYY-MM-DD."})

        # Validate `country_name` against dropdown choices
        country_choices = get_country_choices()
        if country_name and country_name not in country_choices:
            raise ValidationError({"error": f"Invalid country_name. Available choices: {', '.join(country_choices)}"})

        # Initial queryset
        queryset = VaccinationData.objects.all()

        # Filter by country name if provided
        if country_name:
            queryset = queryset.filter(country__name__exact=country_name)

        # Filter by date range if provided
        if start_date and end_date:
            queryset = queryset.filter(first_vaccine_date__range=[start_date, end_date])
        elif start_date:
            queryset = queryset.filter(first_vaccine_date__gte=start_date)
        elif end_date:
            queryset = queryset.filter(first_vaccine_date__lte=end_date)

        # Check if no records are found
        if not queryset.exists():
            return Response({"error": "No vaccination data found for the given filters."}, status=404)

        # Filter unique records manually
        unique_records = {}
        for record in queryset:
            key = (record.country.name, record.total_vaccinations)
            if key not in unique_records:
                unique_records[key] = record

        # Format response
        result = [
            {
                "country_name": record.country.name,
                "total_vaccinations": record.total_vaccinations,
                "persons_vaccinated_first_dose": record.persons_vaccinated_first_dose,
                "persons_last_dose": record.persons_last_dose,
                "persons_booster_add_dose": record.persons_booster_add_dose,
                "first_vaccine_date": record.first_vaccine_date
            }
            for record in unique_records.values()
        ]

        return Response({"count": len(result), "results": result})
