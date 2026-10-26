from django.core.management.base import BaseCommand
from system.models import Resource, GroupResource

class Command(BaseCommand):
    help = 'Initialize all API resources'
    
    def add_arguments(self, parser):
        parser.add_argument('-c', '--clear', dest='clear', 
                          action='store_true', help='Clear before creating')
    
    def handle(self, *args, **options):
        if options['clear']:
            Resource.objects.all().delete()
            self.stdout.write(self.style.WARNING('Cleared all existing resources'))
        
        resources = [
            # Format: (app, name, display_name, url, action, sort, group)
            
            # Customer Management
            ('Customer', 'Customers', 'List', '/api/v1/core/customers/', 'list', '1', 'customer'),
            ('Customer', 'Customers', 'Create', '/api/v1/core/customers/', 'create', '1', 'customer'),
            ('Customer', 'Customers', 'Update', '/api/v1/core/customers/', 'partial_update', '1', 'customer'),
            ('Customer', 'Customers', 'View Detail', '/api/v1/core/customers/', 'retrieve', '1', 'customer'),
            ('Customer', 'Customers', 'Delete', '/api/v1/core/customers/', 'destroy', '1', 'customer'),
            
            # HR Management
            ('ProfileHR', 'Employees', 'List', '/api/v1/core/profile_hrs/', 'list', '2', 'hr'),
            ('ProfileHR', 'Employees', 'Create', '/api/v1/core/profile_hrs/', 'create', '2', 'hr'),
            ('ProfileHR', 'Employees', 'Update', '/api/v1/core/profile_hrs/', 'partial_update', '2', 'hr'),
            ('ProfileHR', 'Employees', 'View Detail', '/api/v1/core/profile_hrs/', 'retrieve', '2', 'hr'),
            ('ProfileHR', 'Employees', 'Delete', '/api/v1/core/profile_hrs/', 'destroy', '2', 'hr'),
            
            # Social Features
            ('SocialPost', 'Posts', 'List', '/api/v1/social/posts/', 'list', '3', 'social'),
            ('SocialPost', 'Posts', 'Create', '/api/v1/social/posts/', 'create', '3', 'social'),
            ('SocialPost', 'Posts', 'Update', '/api/v1/social/posts/', 'partial_update', '3', 'social'),
            ('SocialPost', 'Posts', 'Delete', '/api/v1/social/posts/', 'destroy', '3', 'social'),
            
            # Timekeeping
            ('Attendance', 'Attendance', 'List', '/api/v1/timekeeping/attendance/', 'list', '4', 'timekeeping'),
            ('Attendance', 'Attendance', 'Create', '/api/v1/timekeeping/attendance/', 'create', '4', 'timekeeping'),
            
            # Work Management
            ('Works', 'Works', 'List', '/api/v1/core/works/', 'list', '5', 'work'),
            ('Works', 'Works', 'Create', '/api/v1/core/works/', 'create', '5', 'work'),
            ('Works', 'Works', 'Update', '/api/v1/core/works/', 'partial_update', '5', 'work'),
            ('Works', 'Works', 'Delete', '/api/v1/core/works/', 'destroy', '5', 'work'),
            
            # System Management
            ('Company', 'Companies', 'List', '/api/v1/system/company/', 'list', '6', 'system'),
            ('Company', 'Companies', 'Create', '/api/v1/system/company/', 'create', '6', 'system'),
            ('Company', 'Companies', 'Update', '/api/v1/system/company/', 'partial_update', '6', 'system'),
            
            ('Department', 'Departments', 'List', '/api/v1/system/departments/', 'list', '7', 'system'),
            ('Department', 'Departments', 'Create', '/api/v1/system/departments/', 'create', '7', 'system'),
            ('Department', 'Departments', 'Delete Multiple', '/api/v1/system/departments/', 'delete_departments', '7', 'system'),
            
            ('SystemGroup', 'Groups', 'List', '/api/v1/system/groups/', 'list', '8', 'system'),
            ('SystemGroup', 'Groups', 'Create', '/api/v1/system/groups/', 'create', '8', 'system'),
            ('SystemGroup', 'Groups', 'Update', '/api/v1/system/groups/', 'partial_update', '8', 'system'),
            ('SystemGroup', 'Groups', 'Delete Multiple', '/api/v1/system/groups/', 'delete_groups', '8', 'system'),
            
            ('Permission', 'Permissions', 'List', '/api/v1/system/permissions/', 'list', '9', 'system'),
            ('Permission', 'Permissions', 'Update Multiple', '/api/v1/system/permissions/', 'update_multiple', '9', 'system'),
            
            ('Resource', 'API Resources', 'List', '/api/v1/system/api_resources/', 'list', '10', 'system'),
            ('Resource', 'API Resources', 'Create', '/api/v1/system/api_resources/', 'create', '10', 'system'),
            
            ('GroupResource', 'Resource Groups', 'List', '/api/v1/system/group_resources/', 'list', '11', 'system'),
        ]
        
        created_count = 0
        updated_count = 0
        
        for resource_data in resources:
            apps, name, name_view, url, action, sort, group_code = resource_data
            
            group_resource = GroupResource.objects.filter(group=group_code).first()
            
            obj, created = Resource.objects.update_or_create(
                apps=apps,
                name=name,
                name_view=name_view,
                url=url,
                action=action,
                defaults={
                    'sort_number': sort,
                    'group_resource': group_resource
                }
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Created {created_count} new resources'))
        self.stdout.write(f'✓ Updated {updated_count} existing resources')
        self.stdout.write(self.style.SUCCESS(f'Total resources: {len(resources)}'))
