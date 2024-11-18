from django.core.management.base import BaseCommand
from data_app.models import CovidData
from visualization_app.models import CovidStaticData
from django.db.models import Sum

class Command(BaseCommand):
    help = "Precompute COVID-19 data by country, state, and year"

    def handle(self, *args, **kwargs):
        # Clear existing static data
        CovidStaticData.objects.all().delete()

        # Filter out records with NULL or invalid file_date
        covid_data = CovidData.objects.exclude(file_date__isnull=True)

        # Aggregate COVID-19 data, ensuring unique combinations
        aggregated_data = (
            covid_data.values('country__name', 'province_state', 'country__latitude', 'country__longitude', 'file_date__year')
            .annotate(
                total_deaths=Sum('deaths'),
                total_active=Sum('active'),
                total_confirmed=Sum('confirmed'),
                total_recovered=Sum('recovered'),
            )
            .order_by('country__name', 'province_state', 'file_date__year')
        )

        # Deduplicate entries before inserting
        seen_combinations = set()
        for entry in aggregated_data:
            key = (entry['country__name'], entry['province_state'], entry['file_date__year'])
            if key not in seen_combinations:
                seen_combinations.add(key)
                CovidStaticData.objects.create(
                    country_name=entry['country__name'],
                    state=entry['province_state'],
                    year=entry['file_date__year'],
                    latitude=entry['country__latitude'],
                    longitude=entry['country__longitude'],
                    total_deaths=entry['total_deaths'] or 0,
                    total_active=entry['total_active'] or 0,
                    total_confirmed=entry['total_confirmed'] or 0,
                    total_recovered=entry['total_recovered'] or 0,
                )

        self.stdout.write(self.style.SUCCESS("Successfully precomputed COVID-19 data"))
