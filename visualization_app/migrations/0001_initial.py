# Generated by Django 5.1.3 on 2024-11-19 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CovidStaticData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country_name', models.CharField(max_length=255)),
                ('state', models.CharField(blank=True, max_length=255, null=True)),
                ('year', models.IntegerField(default=2021)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('total_deaths', models.BigIntegerField(default=0)),
                ('total_active', models.BigIntegerField(default=0)),
                ('total_confirmed', models.BigIntegerField(default=0)),
                ('total_recovered', models.BigIntegerField(default=0)),
            ],
            options={
                'unique_together': {('country_name', 'state', 'year')},
            },
        ),
    ]
