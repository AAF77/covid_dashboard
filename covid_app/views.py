from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.pagination import PageNumberPagination
from data_app.models import CovidData
from django.db.models import Sum
from datetime import datetime


class CustomPagination(PageNumberPagination):
    """
    Custom pagination class for paginating COVID-19 data.
    """
    page_size = 20  # Number of records per page
    page_size_query_param = 'page_size'  # Allow user to set page size
    max_page_size = 100  # Limit the maximum records per page


# Helper functions for dropdown options
def get_country_choices():
    return sorted(list(CovidData.objects.values_list('country__name', flat=True).distinct()))


def get_province_choices():
    return sorted(list(CovidData.objects.values_list('province_state', flat=True).distinct()))


class CovidDataFilteredView(APIView):
    """
    Filter and paginate COVID-19 data by country name, province/state, date range, or any combination.
    """
    pagination_class = CustomPagination

    @swagger_auto_schema(
        operation_description="Filter and paginate COVID-19 data by country name, province/state, date range, or any combination.",
        manual_parameters=[
            openapi.Parameter(
                'country_name', openapi.IN_QUERY,
                description="Name of the country to filter by",
                type=openapi.TYPE_STRING,
                enum=get_country_choices()  # Dropdown for country names
            ),
            openapi.Parameter(
                'province_state', openapi.IN_QUERY,
                description="Name of the province/state to filter by (if applicable)",
                type=openapi.TYPE_STRING,
                enum=get_province_choices()  # Dropdown for province names
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
            ),
            openapi.Parameter(
                'page', openapi.IN_QUERY,
                description="Page number for pagination",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'page_size', openapi.IN_QUERY,
                description="Number of records per page (default: 20, max: 100)",
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "count": openapi.Schema(type=openapi.TYPE_INTEGER, description="Total number of records"),
                    "next": openapi.Schema(type=openapi.TYPE_STRING, description="URL of the next page"),
                    "previous": openapi.Schema(type=openapi.TYPE_STRING, description="URL of the previous page"),
                    "results": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "country_name": openapi.Schema(type=openapi.TYPE_STRING, description="Name of the country"),
                                "province_state": openapi.Schema(type=openapi.TYPE_STRING, description="Name of the province/state"),
                                "confirmed": openapi.Schema(type=openapi.TYPE_INTEGER, description="Total confirmed cases"),
                                "deaths": openapi.Schema(type=openapi.TYPE_INTEGER, description="Total deaths"),
                                "recovered": openapi.Schema(type=openapi.TYPE_INTEGER, description="Total recovered cases"),
                                "active": openapi.Schema(type=openapi.TYPE_INTEGER, description="Total active cases"),
                            }
                        )
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
    def get(self, request, *args, **kwargs):
        country_name = request.query_params.get('country_name', None)
        province_state = request.query_params.get('province_state', None)
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)

        # Validate date format
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            except ValueError:
                raise ValidationError({"error": "Invalid start_date format. Use YYYY-MM-DD."})

        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                raise ValidationError({"error": "Invalid end_date format. Use YYYY-MM-DD."})

        if start_date and end_date and start_date > end_date:
            raise ValidationError({"error": "start_date cannot be after end_date."})

        # Initial queryset
        queryset = CovidData.objects.all()

        # Filter by country name if provided
        if country_name:
            queryset = queryset.filter(country__name__exact=country_name)

        # Filter by province/state if provided
        if province_state:
            queryset = queryset.filter(province_state__exact=province_state)

        # Filter by date range if provided
        if start_date and end_date:
            queryset = queryset.filter(file_date__range=[start_date, end_date])
        elif start_date:
            queryset = queryset.filter(file_date__gte=start_date)
        elif end_date:
            queryset = queryset.filter(file_date__lte=end_date)

        # Check if no records are found
        if not queryset.exists():
            return Response({"error": "No COVID-19 data found for the given filters."}, status=404)

        # Aggregate data
        aggregated_data = (
            queryset.values('country__name', 'province_state')
            .annotate(
                confirmed=Sum('confirmed'),
                deaths=Sum('deaths'),
                recovered=Sum('recovered'),
                active=Sum('active')
            )
            .order_by('country__name', 'province_state')
        )

        # Paginate the results
        paginator = CustomPagination()
        paginated_data = paginator.paginate_queryset(aggregated_data, request)
        return paginator.get_paginated_response(paginated_data)
