from django.db import migrations

def create_system_metrics(apps, schema_editor):
    MetricType = apps.get_model('metrics', 'MetricType')
    
    # Delete any existing system metrics to ensure clean state
    MetricType.objects.filter(is_system=True).delete()
    
    metrics = [
        {
            'name': 'Total Shares',
            'category': 'POSITION',
            'data_type': 'SHARES',
            'description': 'Total shares held',
            'is_system': True,
            'is_computed': True,
            'computation_source': 'shares',
            'computation_order': 1
        },
        {
            'name': 'Average Purchase Price',
            'category': 'POSITION',
            'data_type': 'PRICE',
            'description': 'Average price per share',
            'is_system': True,
            'is_computed': True,
            'computation_source': 'avg_price',
            'computation_order': 2
        },
        {
            'name': 'Cost Basis',
            'category': 'POSITION',
            'data_type': 'CURRENCY',
            'description': 'Total cost of position',
            'is_system': True,
            'is_computed': True,
            'computation_source': 'cost_basis',
            'computation_order': 3
        },
        {
            'name': 'Market Price',
            'category': 'MARKET_DATA',
            'data_type': 'PRICE',
            'description': 'Current market price per share',
            'is_system': True,
            'is_computed': False,
            'computation_order': 4
        },
        {
            'name': 'Current Value',
            'category': 'POSITION',
            'data_type': 'CURRENCY',
            'description': 'Current market value of position',
            'is_system': True,
            'is_computed': True,
            'computation_source': 'current_value',
            'computation_order': 5
        },
        {
            'name': 'Position Gain/Loss',
            'category': 'POSITION',
            'data_type': 'PERCENTAGE',
            'description': 'Percentage gain/loss',
            'is_system': True,
            'is_computed': True,
            'computation_source': 'position_gain',
            'computation_order': 6
        }
    ]
    
    created_metrics = {}
    for metric_data in metrics:
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

def remove_system_metrics(apps, schema_editor):
    MetricType = apps.get_model('metrics', 'MetricType')
    MetricType.objects.filter(is_system=True).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('metrics', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_system_metrics, remove_system_metrics),
    ] 