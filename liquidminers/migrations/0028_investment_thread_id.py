# Generated by Django 3.2.9 on 2022-02-25 22:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('liquidminers', '0027_auto_20220224_2305'),
    ]

    operations = [
        migrations.AddField(
            model_name='investment',
            name='thread_id',
            field=models.CharField(default='DEFAULT', max_length=10),
        ),
    ]
