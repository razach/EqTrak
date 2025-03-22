from django.db import migrations, models
import django.db.models.deletion
from django.contrib.contenttypes.fields import GenericForeignKey

class Migration(migrations.Migration):
    initial = True
    
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        # Performance Settings model
        migrations.CreateModel(
            name='PerformanceSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updates_enabled', models.BooleanField(default=True, help_text='Enable or disable performance metrics updates system-wide', verbose_name='Updates Enabled')),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Performance Settings',
                'verbose_name_plural': 'Performance Settings',
            },
        ),
        # Performance Metric model
        migrations.CreateModel(
            name='PerformanceMetric',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('cost_basis', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('current_value', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('absolute_gain_loss', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('percentage_gain_loss', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('calculation_date', models.DateTimeField(auto_now=True)),
                ('is_realized', models.BooleanField(default=False)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
            options={
                'verbose_name': 'Performance Metric',
                'verbose_name_plural': 'Performance Metrics',
            },
        ),
        migrations.AddIndex(
            model_name='performancemetric',
            index=models.Index(fields=['content_type', 'object_id'], name='performance_content_6db675_idx'),
        ),
    ] 