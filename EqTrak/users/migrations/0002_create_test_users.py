from django.db import migrations
from django.contrib.auth.hashers import make_password

def create_test_users(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    
    # Create test_user1
    if not User.objects.filter(username='test_user1').exists():
        User.objects.create(
            username='test_user1',
            email='test_user1@example.com',
            password=make_password('TempPass123!@#'),
            is_staff=True,  # Can access admin
            is_active=True
        )
    
    # Create test_user2
    if not User.objects.filter(username='test_user2').exists():
        User.objects.create(
            username='test_user2',
            email='test_user2@example.com',
            password=make_password('TempPass456!@#'),
            is_staff=True,  # Can access admin
            is_active=True
        )

def delete_test_users(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    User.objects.filter(username__in=['test_user1', 'test_user2']).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_test_users, delete_test_users),
    ] 