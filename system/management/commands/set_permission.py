from django.core.management.base import BaseCommand
from system.models import Permission, SystemGroup

class Command(BaseCommand):
    help = 'Set default permissions for predefined groups'
    
    def handle(self, *args, **options):
        self.stdout.write('Setting default permissions for groups...\n')
        
        # Admin group gets all permissions
        admin_group = SystemGroup.objects.filter(code='admin').first()
        if admin_group:
            updated = Permission.objects.filter(group=admin_group).update(status=True)
            self.stdout.write(self.style.SUCCESS(f'✓ Granted all {updated} permissions to Admin group'))
        else:
            self.stdout.write(self.style.WARNING('! Admin group not found'))
        
        # Manager group gets read + limited write
        manager_group = SystemGroup.objects.filter(code='manager').first()
        if manager_group:
            # Grant read permissions
            read_count = Permission.objects.filter(
                group=manager_group,
                resource__action__in=['list', 'retrieve']
            ).update(status=True)
            
            # Grant specific write permissions
            write_count = Permission.objects.filter(
                group=manager_group,
                resource__apps__in=['Customer', 'Works', 'ProfileHR'],
                resource__action__in=['create', 'partial_update']
            ).update(status=True)
            
            self.stdout.write(self.style.SUCCESS(f'✓ Set Manager permissions: {read_count} read, {write_count} write'))
        else:
            self.stdout.write(self.style.WARNING('! Manager group not found'))
        
        # User group gets limited read
        user_group = SystemGroup.objects.filter(code='user').first()
        if user_group:
            # Grant list permission, exclude system resources
            count = Permission.objects.filter(
                group=user_group,
                resource__action='list'
            ).exclude(
                resource__group_resource__group='system'
            ).update(status=True)
            
            self.stdout.write(self.style.SUCCESS(f'✓ Set User permissions: {count} list permissions'))
        else:
            self.stdout.write(self.style.WARNING('! User group not found'))
        
        self.stdout.write('\n' + self.style.SUCCESS('Permission setup completed!'))
