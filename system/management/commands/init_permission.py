from django.core.management.base import BaseCommand
from system.models import Resource, Permission, SystemGroup

class Command(BaseCommand):
    help = 'Initialize permissions for all groups × resources'
    
    def handle(self, *args, **options):
        confirm = input('This will create permissions for all groups × resources. Continue? [Y/n]: ')
        if confirm != 'Y':
            self.stdout.write('Cancelled')
            return
        
        resources = Resource.objects.all()
        groups = SystemGroup.objects.all()
        
        if not resources.exists():
            self.stdout.write(self.style.ERROR('No resources found. Please run init_resource first.'))
            return
        
        if not groups.exists():
            self.stdout.write(self.style.ERROR('No groups found. Please create SystemGroups first.'))
            return
        
        count = 0
        created_count = 0
        for resource in resources:
            for group in groups:
                obj, created = Permission.objects.get_or_create(
                    resource=resource,
                    group=group,
                    defaults={'status': False}  # Default deny
                )
                if created:
                    created_count += 1
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Created {created_count} new permissions'))
        self.stdout.write(f'Total permissions: {count}')
