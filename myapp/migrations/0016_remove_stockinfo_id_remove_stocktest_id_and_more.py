# Generated by Django 4.0.6 on 2022-09-30 06:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0015_stocktest_avg_volume_float_stocktest_book_value_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stockinfo',
            name='id',
        ),
        migrations.RemoveField(
            model_name='stocktest',
            name='id',
        ),
        migrations.AlterField(
            model_name='stockinfo',
            name='name',
            field=models.TextField(default='default', primary_key=b'I01\n', serialize=False),
        ),
        migrations.AlterField(
            model_name='stocktest',
            name='name',
            field=models.TextField(default='Ticker', primary_key=b'I01\n', serialize=False),
        ),
    ]
