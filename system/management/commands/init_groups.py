from django.core.management.base import BaseCommand
from system.models import SystemGroup

class Command(BaseCommand):
    help = 'Initialize default system groups (Admin, Manager, User)'
    
    def handle(self, *args, **options):
        groups = [
            {
                'name': 'Admin',
                'code': 'admin',
                'description': 'Full system access with all permissions'
            },
            {
                'name': 'Manager',
                'code': 'manager',
                'description': 'Department managers with limited write access'
            },
            {
                'name': 'User',
                'code': 'user',
                'description': 'Regular users with read-only access'
            },
        ]
        
        created_count = 0
        updated_count = 0
        for group_data in groups:
            obj, created = SystemGroup.objects.update_or_create(
                code=group_data['code'],
                defaults={
                    'name': group_data['name'],
                    'description': group_data['description'],
                    'fixed_group': True
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created: {group_data["name"]} ({group_data["code"]})'))
            else:
                updated_count += 1
                self.stdout.write(f'Already exists / Updated: {group_data["name"]} ({group_data["code"]})')
        
        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully created {created_count} and updated {updated_count} system groups'))
        
        if created_count > 0:
            self.stdout.write('\n' + self.style.WARNING('⚠ Remember to run: python3 manage.py set_permission'))
