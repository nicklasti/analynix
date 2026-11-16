from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0045_missing_values_as_null"),
    ]

    operations = [
        migrations.AddField(
            model_name="stockinfo",
            name="peer_groups",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
