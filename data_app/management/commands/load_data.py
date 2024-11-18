# File: data_app/management/commands/load_data.py

import csv
import time
from datetime import datetime
from django.core.management.base import BaseCommand
from data_app.models import Country, CovidData, VaccinationData


class Command(BaseCommand):
    help = "Load data from normalized CSV files into the database"

    def handle(self, *args, **kwargs):
        countries_csv = "D:/YCB/Public Health Insights from COVID-19 Data/DataSet/src/countries.csv"
        vaccination_data_csv = "D:/YCB/Public Health Insights from COVID-19 Data/DataSet/src/vaccination_data.csv"
        covid_data_csv = "D:/YCB/Public Health Insights from COVID-19 Data/DataSet/src/covid_data.csv"

        # Load countries
        self.stdout.write("Loading countries...")
        start_time = time.time()
        self.load_countries(countries_csv)
        elapsed_time = time.time() - start_time
        self.stdout.write(self.style.SUCCESS(f"Countries loaded in {elapsed_time:.2f} seconds."))

        # Load vaccination data
        self.stdout.write("Loading vaccination data...")
        start_time = time.time()
        self.load_vaccination_data(vaccination_data_csv)
        elapsed_time = time.time() - start_time
        self.stdout.write(self.style.SUCCESS(f"Vaccination data loaded in {elapsed_time:.2f} seconds."))

        # Load COVID-19 data
        self.stdout.write("Loading COVID-19 data...")
        start_time = time.time()
        self.load_covid_data(covid_data_csv)
        elapsed_time = time.time() - start_time
        self.stdout.write(self.style.SUCCESS(f"COVID-19 data loaded in {elapsed_time:.2f} seconds."))

    def load_countries(self, file_path):
        batch_size = 1000
        countries = []
        with open(file_path, "r") as f:
            reader = csv.DictReader(f, delimiter=",")
            for row in reader:
                if not row["id"] or not row["Country_Region"]:
                    continue
                try:
                    countries.append(
                        Country(
                            id=int(float(row["id"])),
                            name=row["Country_Region"].strip(),
                            latitude=float(row["Lat"]) if row["Lat"] else None,
                            longitude=float(row["Long_"]) if row["Long_"] else None,
                        )
                    )
                    if len(countries) >= batch_size:
                        Country.objects.bulk_create(countries, ignore_conflicts=True)
                        countries.clear()
                except Exception as e:
                    self.stderr.write(f"Error processing country: {row} -> {e}")
            if countries:
                Country.objects.bulk_create(countries, ignore_conflicts=True)

    def load_vaccination_data(self, file_path):
        batch_size = 1000
        vaccinations = []
        with open(file_path, "r") as f:
            reader = csv.DictReader(f, delimiter=",")
            for row in reader:
                if not row["country_id"]:  # Skip rows with missing country_id
                    continue
                try:
                    country = Country.objects.get(id=int(float(row["country_id"])))
                    vaccinations.append(
                        VaccinationData(
                            country=country,
                            total_vaccinations=int(row["total_vaccinations"]) if row["total_vaccinations"] else 0,
                            persons_vaccinated_first_dose=int(row["persons_vaccinated_first_dose"]) if row["persons_vaccinated_first_dose"] else 0,
                            persons_last_dose=int(row["persons_last_dose"]) if row["persons_last_dose"] else 0,
                            persons_booster_add_dose=int(row["persons_booster_add_dose"]) if row["persons_booster_add_dose"] else 0,
                            first_vaccine_date=datetime.strptime(row["first_vaccine_date"], "%m/%d/%Y").date() if row["first_vaccine_date"] else None,
                        )
                    )
                    if len(vaccinations) >= batch_size:
                        VaccinationData.objects.bulk_create(vaccinations)
                        vaccinations.clear()
                except Exception as e:
                    self.stderr.write(f"Error processing vaccination data: {row} -> {e}")
            if vaccinations:
                VaccinationData.objects.bulk_create(vaccinations)

    def load_covid_data(self, file_path):
        batch_size = 5000
        covid_records = []
        with open(file_path, "r") as f:
            reader = csv.DictReader(f, delimiter=",")
            for row in reader:
                if not row["country_id"]:  # Skip rows with missing country_id
                    continue
                try:
                    country = Country.objects.get(id=int(float(row["country_id"])))
                    covid_records.append(
                        CovidData(
                            country=country,
                            province_state=row["Province_State"].strip() if row["Province_State"] else None,
                            confirmed=int(float(row["Confirmed"])) if row["Confirmed"] else 0,
                            deaths=int(float(row["Deaths"])) if row["Deaths"] else 0,
                            recovered=int(float(row["Recovered"])) if row["Recovered"] else 0,
                            active=int(float(row["Active"])) if row["Active"] else 0,
                            incident_rate=float(row["Incident_Rate"]) if row["Incident_Rate"] else None,
                            case_fatality_ratio=float(row["Case_Fatality_Ratio"]) if row["Case_Fatality_Ratio"] else None,
                            file_date=datetime.strptime(row["File_Date"], "%Y-%m-%d").date() if row["File_Date"] else None,
                        )
                    )
                    if len(covid_records) >= batch_size:
                        CovidData.objects.bulk_create(covid_records)
                        covid_records.clear()
                except Exception as e:
                    self.stderr.write(f"Error processing COVID-19 data: {row} -> {e}")
            if covid_records:
                CovidData.objects.bulk_create(covid_records)
