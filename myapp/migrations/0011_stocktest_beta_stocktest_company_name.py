# Generated by Django 4.0.6 on 2022-09-22 05:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0010_stocktest'),
    ]

    operations = [
        migrations.AddField(
            model_name='stocktest',
            name='beta',
            field=models.TextField(default=0),
        ),
        migrations.AddField(
            model_name='stocktest',
            name='company_name',
            field=models.TextField(default='Company Name'),
        ),
    ]
