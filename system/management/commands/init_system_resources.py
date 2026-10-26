from django.core.management.base import BaseCommand
from system.models import SystemResource, SystemGroup


class Command(BaseCommand):
    help = 'Initialize system resources and admin group'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting system resources initialization...'))
        
        # Define the system resources (codes align with enabled_modules and MODULE_URL_MAP)
        resources_data = [
            {
                'name': 'Hướng dẫn Mail',
                'code': 'guide_mail',
                'apps': 'mail',
                'description': 'Mail guide and documentation'
            },
            {
                'name': 'Hướng dẫn App',
                'code': 'guide_app',
                'apps': 'app',
                'description': 'App guide and documentation'
            },
            {
                'name': 'Tác vụ',
                'code': 'task',
                'apps': 'mail',
                'description': 'Task management resources'
            },
            {
                'name': 'Nhân sự',
                'code': 'hrm',        # was 'customer' — renamed to align with enabled_modules
                'apps': 'me, profile_hr',
                'description': 'Human resources and profile management'
            },
            {
                'name': 'Bán hàng',
                'code': 'crm',
                'apps': 'contact, customer',
                'description': 'CRM and sales resources'
            },
            {
                'name': 'Workspace',
                'code': 'workspace',
                'apps': 'work, schedule_event, dashboard, social',
                'description': 'Workspace and collaboration resources'
            },
            {
                'name': 'Công ty',
                'code': 'company',
                'apps': 'company',
                'description': 'Company management resources'
            },
        ]
        
        # Create or update the resources
        created_resources = []
        for resource_data in resources_data:
            try:
                resource, created = SystemResource.objects.update_or_create(
                    code=resource_data['code'],
                    defaults={
                        'name': resource_data['name'],
                        'apps': resource_data['apps'],
                        'description': resource_data['description']
                    }
                )
            except SystemResource.MultipleObjectsReturned:
                # Handle duplicates if they exist in the DB
                duplicates = SystemResource.objects.filter(code=resource_data['code'])
                resource = duplicates.first()
                # Update the first one
                for key, value in {
                    'name': resource_data['name'],
                    'apps': resource_data['apps'],
                    'description': resource_data['description']
                }.items():
                    setattr(resource, key, value)
                resource.save()
                # Delete the rest
                duplicates.exclude(id=resource.id).delete()
                created = False
            
            created_resources.append(resource)
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created resource: {resource.name} ({resource.code})')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⟳ Updated resource: {resource.name} ({resource.code})')
                )
        
        self.stdout.write(self.style.SUCCESS(f'\nTotal resources processed: {len(created_resources)}'))
        
        # Create or update the admin group
        admin_group, created = SystemGroup.objects.update_or_create(
            code='ADM',
            defaults={
                'name': 'Nhóm admin',
                'description': 'Administrator group with full access to all system resources'
            }
        )
        
        # Add all resources to the admin group
        admin_group.resources.set(created_resources)
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'\n✓ Created group: {admin_group.name} ({admin_group.code})')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'\n⟳ Updated group: {admin_group.name} ({admin_group.code})')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'✓ Added {admin_group.resources.count()} resources to {admin_group.name}')
        )
        
        # Display summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('INITIALIZATION COMPLETE'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(f'\nSystem Resources created: {len(created_resources)}')
        self.stdout.write(f'Admin Group: {admin_group.name}')
        self.stdout.write(f'Resources in admin group: {admin_group.resources.count()}')
        
        # List all resources in the group
        self.stdout.write(self.style.SUCCESS('\nResources in admin group:'))
        for idx, resource in enumerate(admin_group.resources.all(), start=1):
            self.stdout.write(f'  {idx}. {resource.name} ({resource.code}) - Apps: {resource.apps}')
