from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("admissions", "0002_expand_categories"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cutoff",
            name="min_score",
            field=models.DecimalField(decimal_places=2, max_digits=8),
        ),
        migrations.AlterField(
            model_name="cutoff",
            name="max_score",
            field=models.DecimalField(decimal_places=2, max_digits=8),
        ),
        migrations.AddField(
            model_name="cutoff",
            name="metric_type",
            field=models.CharField(
                choices=[("score", "Score"), ("marks", "Marks")],
                default="score",
                max_length=8,
            ),
        ),
    ]
