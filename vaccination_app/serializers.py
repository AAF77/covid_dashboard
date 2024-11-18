from rest_framework import serializers
from data_app.models import VaccinationData

class VaccinationDataSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)

    class Meta:
        model = VaccinationData
        fields = [
            'id',
            'country_name',
            'total_vaccinations',
            'persons_vaccinated_first_dose',
            'persons_last_dose',
            'persons_booster_add_dose',
            'first_vaccine_date',
        ]
