# Generated by Django 3.2.9 on 2022-03-01 21:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('liquidminers', '0034_pool_max_spread'),
    ]

    operations = [
        migrations.AlterField(
            model_name='investment',
            name='thread_id',
            field=models.CharField(default='RELEASED', max_length=10),
        ),
    ]
