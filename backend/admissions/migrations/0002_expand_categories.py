from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("admissions", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="applicantsession",
            name="category",
            field=models.CharField(
                choices=[
                    ("GENERAL", "General"),
                    ("GENERAL_PWD", "General PwD"),
                    ("OBC_NCL", "OBC-NCL"),
                    ("OBC_NCL_PWD", "OBC-NCL PwD"),
                    ("SC", "SC"),
                    ("SC_PWD", "SC PwD"),
                    ("ST", "ST"),
                    ("ST_PWD", "ST PwD"),
                    ("EWS", "EWS"),
                    ("EWS_PWD", "EWS PwD"),
                ],
                max_length=12,
            ),
        ),
        migrations.AlterField(
            model_name="cutoff",
            name="category",
            field=models.CharField(
                choices=[
                    ("GENERAL", "General"),
                    ("GENERAL_PWD", "General PwD"),
                    ("OBC_NCL", "OBC-NCL"),
                    ("OBC_NCL_PWD", "OBC-NCL PwD"),
                    ("SC", "SC"),
                    ("SC_PWD", "SC PwD"),
                    ("ST", "ST"),
                    ("ST_PWD", "ST PwD"),
                    ("EWS", "EWS"),
                    ("EWS_PWD", "EWS PwD"),
                ],
                max_length=12,
            ),
        ),
    ]
