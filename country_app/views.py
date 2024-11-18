from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from data_app.models import CovidData


# Helper functions for dropdown options
def get_country_choices():
    return sorted(list(CovidData.objects.values_list('country__name', flat=True).distinct()))


def get_province_choices():
    return sorted(list(CovidData.objects.values_list('province_state', flat=True).distinct()))


class CountrySearchView(APIView):
    """
    Search for countries by province/state or provinces by country.
    If both `country_name` and `province_state` are provided, returns the record where both conditions are true.
    """
    @swagger_auto_schema(
        operation_description="Search for countries by province/state or provinces by country. If both `country_name` and `province_state` are provided, returns the record where both conditions are true.",
        manual_parameters=[
            openapi.Parameter(
                'country_name', openapi.IN_QUERY,
                description="Filter by country name",
                type=openapi.TYPE_STRING,
                enum=get_country_choices()  # Dropdown for country names
            ),
            openapi.Parameter(
                'province_state', openapi.IN_QUERY,
                description="Filter by province/state name",
                type=openapi.TYPE_STRING,
                enum=get_province_choices()  # Dropdown for province/state names
            )
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "country_name": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Name of the country"
                    ),
                    "province_states": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_STRING),
                        description="List of provinces/states in the country"
                    ),
                    "matched_records": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "country_name": openapi.Schema(type=openapi.TYPE_STRING, description="Name of the country"),
                                "province_state": openapi.Schema(type=openapi.TYPE_STRING, description="Name of the province/state"),
                            }
                        ),
                        description="List of matched records if both filters are applied"
                    )
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
    def get(self, request):
        country_name = request.query_params.get('country_name', None)
        province_state = request.query_params.get('province_state', None)

        # Validate input
        if not country_name and not province_state:
            return Response(
                {"error": "You must provide either 'country_name' or 'province_state' as a query parameter."},
                status=400
            )

        # If both country_name and province_state are provided, filter where both are true
        if country_name and province_state:
            matched_records = CovidData.objects.filter(
                country__name__exact=country_name,
                province_state__exact=province_state
            ).values('country__name', 'province_state')
            if not matched_records.exists():
                return Response({"error": f"No matching records found for country: {country_name} and province/state: {province_state}"}, status=404)
            return Response({
                "matched_records": list(matched_records)
            })

        # Search by country_name
        if country_name:
            provinces = CovidData.objects.filter(country__name__exact=country_name).values_list('province_state', flat=True).distinct()
            if not provinces.exists():
                return Response({"error": f"No provinces found for country: {country_name}"}, status=404)
            return Response({
                "country_name": country_name,
                "province_states": list(provinces)
            })

        # Search by province_state
        if province_state:
            countries = CovidData.objects.filter(province_state__exact=province_state).values_list('country__name', flat=True).distinct()
            if not countries.exists():
                return Response({"error": f"No countries found for province/state: {province_state}"}, status=404)
            return Response({
                "province_state": province_state,
                "countries": list(countries)
            })
