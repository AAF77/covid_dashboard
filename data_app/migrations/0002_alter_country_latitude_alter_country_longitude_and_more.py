# Generated by Django 5.1.3 on 2024-11-17 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='country',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='country',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='coviddata',
            name='active',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='coviddata',
            name='confirmed',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='coviddata',
            name='deaths',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='coviddata',
            name='file_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='coviddata',
            name='recovered',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='vaccinationdata',
            name='first_vaccine_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='vaccinationdata',
            name='persons_booster_add_dose',
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='vaccinationdata',
            name='persons_last_dose',
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='vaccinationdata',
            name='persons_vaccinated_first_dose',
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='vaccinationdata',
            name='total_vaccinations',
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]