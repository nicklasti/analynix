# Generated by Django 4.0.6 on 2022-09-22 03:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0008_industryinfo_avg_mkt_cap_industryinfo_ind_size'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stockinfo',
            old_name='ticker',
            new_name='name',
        ),
    ]
