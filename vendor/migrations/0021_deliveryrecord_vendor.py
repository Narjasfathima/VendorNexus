# Generated by Django 4.2.7 on 2023-12-02 12:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0020_alter_purchaseorder_acknowledgment_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliveryrecord',
            name='vendor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='vendor.vendor'),
        ),
    ]
