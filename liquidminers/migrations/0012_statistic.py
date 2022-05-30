# Generated by Django 3.2.9 on 2021-12-28 19:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('liquidminers', '0011_alter_order_worth'),
    ]

    operations = [
        migrations.CreateModel(
            name='Statistic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lookup_id', models.IntegerField(default=0, null=True)),
                ('value', models.FloatField(null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='liquidminers.pair')),
            ],
        ),
    ]
