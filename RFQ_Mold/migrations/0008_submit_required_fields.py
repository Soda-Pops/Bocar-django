from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RFQ_Mold', '0007_remove_rfq_mold_selected_supplier'),
    ]

    operations = [
        migrations.AddField(
            model_name='rfq_mold',
            name='part_name',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='rfq_mold',
            name='three_plate_mold',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
