from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RFQ_Trimming', '0006_remove_rfq_trimming_selected_supplier'),
    ]

    operations = [
        migrations.AddField(
            model_name='rfq_trimming',
            name='supplier',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]
