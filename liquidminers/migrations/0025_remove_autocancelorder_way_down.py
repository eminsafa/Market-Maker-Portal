# Generated by Django 3.2.9 on 2022-02-24 19:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('liquidminers', '0024_orderconfig_balance_allocation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='autocancelorder',
            name='way_down',
        ),
    ]
