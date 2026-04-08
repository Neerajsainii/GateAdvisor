from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("admissions", "0004_payment_plan_code"),
    ]

    operations = [
        migrations.AddField(
            model_name="applicantsession",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name="applicant_sessions",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
