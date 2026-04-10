from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("admissions", "0005_applicantsession_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="payment",
            name="subscription_expires_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="payment",
            name="subscription_started_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
