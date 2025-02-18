# Generated by Django 5.1.5 on 2025-02-09 00:33

import django.core.validators
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('portfolio', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MetricType',
            fields=[
                ('metric_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('category', models.CharField(choices=[('MARKET_DATA', 'Market Data'), ('FUNDAMENTAL', 'Fundamental'), ('TECHNICAL', 'Technical'), ('POSITION', 'Position')], max_length=20)),
                ('data_type', models.CharField(choices=[('PRICE', 'Price'), ('RATIO', 'Ratio'), ('VOLUME', 'Volume'), ('PERCENTAGE', 'Percentage'), ('SHARES', 'Shares'), ('CURRENCY', 'Currency')], max_length=20)),
                ('description', models.TextField(blank=True, null=True)),
                ('is_system', models.BooleanField(default=False)),
                ('is_computed', models.BooleanField(default=False)),
                ('computation_source', models.CharField(blank=True, choices=[('shares', 'Total Shares'), ('avg_price', 'Average Price'), ('cost_basis', 'Cost Basis'), ('current_value', 'Current Value'), ('position_gain', 'Position Gain/Loss')], max_length=50, null=True)),
                ('computation_order', models.IntegerField(default=0)),
                ('computation_dependencies', models.ManyToManyField(blank=True, to='metrics.metrictype')),
            ],
            options={
                'ordering': ['computation_order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='MetricValue',
            fields=[
                ('value_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('date', models.DateField()),
                ('value', models.DecimalField(decimal_places=6, max_digits=15)),
                ('source', models.CharField(default='USER', max_length=50)),
                ('confidence', models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('is_forecast', models.BooleanField(default=False)),
                ('scenario', models.CharField(blank=True, choices=[('BASE', 'Base Case'), ('BULL', 'Bull Case'), ('BEAR', 'Bear Case')], max_length=10, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('metric_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metrics.metrictype')),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portfolio.position')),
            ],
            options={
                'ordering': ['-date', '-created_at'],
            },
        ),
    ]
