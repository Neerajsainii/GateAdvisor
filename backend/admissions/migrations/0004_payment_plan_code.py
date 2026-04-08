from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("admissions", "0003_cutoff_metric_decimal"),
    ]

    operations = [
        migrations.AddField(
            model_name="payment",
            name="plan_code",
            field=models.CharField(default="weekly", max_length=24),
        ),
    ]
