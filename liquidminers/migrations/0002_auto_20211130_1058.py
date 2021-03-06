# Generated by Django 3.2.9 on 2021-11-30 10:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('liquidminers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Configuration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, unique=True, verbose_name='Name')),
                ('value', models.CharField(max_length=128, null=True, verbose_name='Value')),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='salt',
            field=models.CharField(default='gknvmnewgyoqeuivcpdpuhfbrqfwctmc', max_length=32),
        ),
        migrations.AlterField(
            model_name='credential',
            name='exchange',
            field=models.CharField(max_length=32, null=True),
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reward', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='liquidminers.pool')),
                ('status', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='liquidminers.status')),
                ('week', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='liquidminers.week')),
            ],
        ),
        migrations.CreateModel(
            name='RewardSharing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ratio', models.FloatField(default=0.0)),
                ('amount', models.FloatField(default=0.0)),
                ('investment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='liquidminers.investment')),
                ('pool', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='liquidminers.pool')),
                ('week', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='liquidminers.week')),
            ],
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True, null=True)),
                ('type', models.CharField(default='INFO', max_length=16, null=True)),
                ('message', models.TextField()),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='APILog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True, null=True)),
                ('endpoint', models.CharField(max_length=128, null=True)),
                ('params', models.TextField()),
                ('response', models.TextField()),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
