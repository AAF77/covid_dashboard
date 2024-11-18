# Generated by Django 5.1.3 on 2024-11-17 22:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_app', '0005_alter_coviddata_country'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coviddata',
            name='file_date',
            field=models.DateField(blank=True, db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='coviddata',
            name='province_state',
            field=models.CharField(blank=True, db_index=True, max_length=255, null=True),
        ),
        migrations.AddIndex(
            model_name='coviddata',
            index=models.Index(fields=['country', 'province_state'], name='data_app_co_country_74e480_idx'),
        ),
        migrations.AddIndex(
            model_name='coviddata',
            index=models.Index(fields=['file_date'], name='data_app_co_file_da_b717ec_idx'),
        ),
    ]
