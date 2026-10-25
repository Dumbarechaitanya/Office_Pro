import base.fields
from django.db import migrations


class Migration(migrations.Migration):
    """Store the SMTP password encrypted at rest (see base/fields.py). Widens the column to 512."""

    dependencies = [
        ('base', '0018_delete_employee'),
    ]

    operations = [
        migrations.AlterField(
            model_name='irmailserver',
            name='smtp_pass',
            field=base.fields.EncryptedCharField(
                blank=True, null=True, max_length=512,
                help_text='Password/App Password for SMTP authentication (stored encrypted)',
            ),
        ),
    ]
