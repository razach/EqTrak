from django.db import migrations, models
import django.core.validators
import django.db.models.deletion
import uuid

def create_system_metrics(apps, schema_editor):
    MetricType = apps.get_model('metrics', 'MetricType')
    
    system_metrics = [
        # Position metrics
        {
            'name': 'Total Shares',
            'scope_type': 'POSITION',
            'data_type': 'SHARES',
            'description': 'Total shares held',
            'is_system': True,
            'tags': 'System,Computed',
            'is_computed': True,
            'computation_source': 'shares',
            'computation_order': 1
        },
        {
            'name': 'Average Purchase Price',
            'scope_type': 'POSITION',
            'data_type': 'PRICE',
            'description': 'Average price per share',
            'is_system': True,
            'tags': 'System,Computed',
            'is_computed': True,
            'computation_source': 'avg_price',
            'computation_order': 2
        },
        {
            'name': 'Cost Basis',
            'scope_type': 'POSITION',
            'data_type': 'CURRENCY',
            'description': 'Total cost of position',
            'is_system': True,
            'tags': 'System,Computed',
            'is_computed': True,
            'computation_source': 'cost_basis',
            'computation_order': 3
        },
        {
            'name': 'Market Price',
            'scope_type': 'POSITION',
            'data_type': 'PRICE',
            'description': 'Current market price per share',
            'is_system': True,
            'tags': 'System',
            'is_computed': False,
            'computation_order': 4
        },
        {
            'name': 'Current Value',
            'scope_type': 'POSITION',
            'data_type': 'CURRENCY',
            'description': 'Current market value of position',
            'is_system': True,
            'tags': 'System,Computed',
            'is_computed': True,
            'computation_source': 'current_value',
            'computation_order': 5
        },
        {
            'name': 'Position Gain/Loss',
            'scope_type': 'POSITION',
            'data_type': 'PERCENTAGE',
            'description': 'Percentage gain/loss',
            'is_system': True,
            'tags': 'System,Computed',
            'is_computed': True,
            'computation_source': 'position_gain',
            'computation_order': 6
        },
        # Portfolio metrics
        {
            'name': 'Total Portfolio Value',
            'scope_type': 'PORTFOLIO',
            'data_type': 'CURRENCY',
            'description': 'Total value of all positions plus cash',
            'is_system': True,
            'tags': 'System,Computed',
            'is_computed': True,
            'computation_source': 'total_value',
            'computation_order': 10
        },
        {
            'name': 'Cash Balance',
            'scope_type': 'PORTFOLIO',
            'data_type': 'CURRENCY',
            'description': 'Available cash in portfolio',
            'is_system': True,
            'tags': 'System',
            'is_computed': False,
            'computation_order': 11
        },
        {
            'name': 'Portfolio Return',
            'scope_type': 'PORTFOLIO',
            'data_type': 'PERCENTAGE',
            'description': 'Total portfolio return percentage',
            'is_system': True,
            'tags': 'System,Computed',
            'is_computed': True,
            'computation_source': 'portfolio_return',
            'computation_order': 12
        },
        # Transaction metrics
        {
            'name': 'Transaction Impact',
            'scope_type': 'TRANSACTION',
            'data_type': 'CURRENCY',
            'description': 'Total impact of transaction including fees',
            'is_system': True,
            'tags': 'System,Computed',
            'is_computed': True,
            'computation_source': 'transaction_impact',
            'computation_order': 20
        },
        {
            'name': 'Fee Percentage',
            'scope_type': 'TRANSACTION',
            'data_type': 'PERCENTAGE',
            'description': 'Transaction fees as percentage of value',
            'is_system': True,
            'tags': 'System,Computed',
            'is_computed': True,
            'computation_source': 'fee_percentage',
            'computation_order': 21
        }
    ]
    
    # Create all system metrics
    created_metrics = {}
    for metric_data in system_metrics:
        metric_data['metric_id'] = uuid.uuid4()
        created_metrics[metric_data['name']] = MetricType.objects.create(**metric_data)
    
    # Set up dependencies
    created_metrics['Cost Basis'].computation_dependencies.add(
        created_metrics['Total Shares'],
        created_metrics['Average Purchase Price']
    )
    created_metrics['Current Value'].computation_dependencies.add(
        created_metrics['Total Shares'],
        created_metrics['Market Price']
    )
    created_metrics['Position Gain/Loss'].computation_dependencies.add(
        created_metrics['Cost Basis'],
        created_metrics['Current Value']
    )
    created_metrics['Portfolio Return'].computation_dependencies.add(
        created_metrics['Total Portfolio Value'],
        created_metrics['Cash Balance']
    )

def reverse_system_metrics(apps, schema_editor):
    MetricType = apps.get_model('metrics', 'MetricType')
    MetricType.objects.filter(is_system=True).delete()

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
                ('scope_type', models.CharField(choices=[('POSITION', 'Position'), ('TRANSACTION', 'Transaction'), ('PORTFOLIO', 'Portfolio')], default='POSITION', max_length=20)),
                ('data_type', models.CharField(choices=[('PRICE', 'Price'), ('RATIO', 'Ratio'), ('VOLUME', 'Volume'), ('PERCENTAGE', 'Percentage'), ('SHARES', 'Shares'), ('CURRENCY', 'Currency'), ('MEMO', 'Memo')], max_length=20)),
                ('description', models.TextField(blank=True, null=True)),
                ('is_system', models.BooleanField(default=False)),
                ('tags', models.CharField(blank=True, help_text='Comma-separated tags for organization', max_length=200, null=True)),
                ('is_computed', models.BooleanField(default=False)),
                ('computation_source', models.CharField(blank=True, choices=[('shares', 'Total Shares'), ('avg_price', 'Average Price'), ('cost_basis', 'Cost Basis'), ('current_value', 'Current Value'), ('position_gain', 'Position Gain/Loss'), ('total_value', 'Total Portfolio Value'), ('cash_balance', 'Cash Balance'), ('portfolio_return', 'Portfolio Return'), ('transaction_impact', 'Transaction Impact'), ('fee_percentage', 'Fee Percentage')], max_length=50, null=True)),
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
                ('value', models.DecimalField(decimal_places=6, max_digits=15, null=True, blank=True)),
                ('text_value', models.TextField(null=True, blank=True, help_text="Text content for memo-type metrics")),
                ('source', models.CharField(default='USER', max_length=50)),
                ('confidence', models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('is_forecast', models.BooleanField(default=False)),
                ('scenario', models.CharField(blank=True, choices=[('BASE', 'Base Case'), ('BULL', 'Bull Case'), ('BEAR', 'Bear Case')], max_length=10, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('metric_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metrics.metrictype')),
                ('position', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='portfolio.position')),
                ('portfolio', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='portfolio.portfolio')),
                ('transaction', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='portfolio.transaction')),
            ],
            options={
                'ordering': ['-date', '-created_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='metricvalue',
            constraint=models.CheckConstraint(
                check=(
                    (models.Q(position__isnull=False) & models.Q(portfolio__isnull=True) & models.Q(transaction__isnull=True)) |
                    (models.Q(position__isnull=True) & models.Q(portfolio__isnull=False) & models.Q(transaction__isnull=True)) |
                    (models.Q(position__isnull=True) & models.Q(portfolio__isnull=True) & models.Q(transaction__isnull=False))
                ),
                name='metric_value_single_target'
            ),
        ),
        migrations.RunPython(create_system_metrics, reverse_system_metrics),
    ] 