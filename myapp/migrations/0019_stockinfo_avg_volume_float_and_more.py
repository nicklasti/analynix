# Generated by Django 4.0.6 on 2022-09-30 21:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0018_delete_stocktest'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockinfo',
            name='avg_volume_float',
            field=models.FloatField(default=69.69),
        ),
        migrations.AlterField(
            model_name='stockinfo',
            name='avg_volume',
            field=models.TextField(default='default'),
        ),
    ]