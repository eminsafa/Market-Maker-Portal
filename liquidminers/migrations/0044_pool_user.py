# Generated by Django 3.2.9 on 2022-04-03 11:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('liquidminers', '0043_investment_param_update_check'),
    ]

    operations = [
        migrations.AddField(
            model_name='pool',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]