# Generated by Django 3.2.9 on 2021-12-21 00:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('liquidminers', '0007_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pool',
            name='campaign_duration',
        ),
    ]
