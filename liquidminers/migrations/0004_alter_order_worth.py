# Generated by Django 3.2.9 on 2021-12-04 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('liquidminers', '0003_remove_week_wid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='worth',
            field=models.FloatField(null=True),
        ),
    ]
