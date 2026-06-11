from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('RFQ_Trimming', '0007_submit_required_fields'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rfq_trimming',
            name='supplier',
        ),
    ]
