from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("admissions", "0002_payment_subscription_window"),
    ]

    operations = [
        migrations.AddField(
            model_name="payment",
            name="subscription_days",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
