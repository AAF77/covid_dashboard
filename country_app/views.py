from rest_framework.response import Response
from rest_framework.views import APIView
from data_app.models import CovidData
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class CountriesView(APIView):
    """
    Retrieves a list of all unique country names available in the dataset.
    """

    @swagger_auto_schema(
        operation_description="Retrieves a list of all unique country names available in the dataset.",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_STRING),
                description="List of unique country names"
            ),
            404: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "error": openapi.Schema(type=openapi.TYPE_STRING, description="No countries found")
                }
            )
        }
    )
    def get(self, request):
        # Retrieve all unique country names from the CovidData model
        country_names = CovidData.objects.values_list('country__name', flat=True).distinct()

        # Check if there are any countries in the dataset
        if not country_names.exists():
            return Response({"error": "No countries found in the dataset."}, status=404)

        # Return the list of country names
        return Response(list(country_names), status=200)
