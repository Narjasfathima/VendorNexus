# Generated by Django 4.2.7 on 2023-11-26 06:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0004_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vendor',
            name='user',
        ),
    ]
