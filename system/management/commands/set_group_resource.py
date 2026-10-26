from django.core.management.base import BaseCommand
from system.models import GroupResource, Resource

class Command(BaseCommand):
    help = 'Link resources to their group resource categories'

    def handle(self, *args, **options):
        # Define which apps belong to which group resource category
        resource_mappings = {
            'hr': (
                'ProfileHR', 'Title', 'Position', 'Nationality', 
                'Bank', 'FamilyRelationship', 'ProfessionalQualification'
            ),
            'customer': (
                'Customer', 'CustomerAttachment', 'CustomerComment', 
                'ContactAddtionalInfo'
            ),
            'social': (
                'SocialPost', 'SocialComment', 'SocialLike', 'SocialShare'
            ),
            'work': (
                'Works', 'WorkAttachment', 'WorkComment'
            ),
            'timekeeping': (
                'Attendance', 'TimeSheet', 'Leave', 'Overtime'
            ),
            'system': (
                'Company', 'Department', 'SystemGroup', 'Permission', 
                'Resource', 'GroupResource', 'BusinessUnit', 'ConfigVolume',
                'SystemResource'
            ),
            'analytics': (
                'Report', 'Dashboard', 'Analytics'
            ),
            'consult': (
                'Consultation', 'ConsultRequest'
            ),
        }

        updated_count = 0
        
        for group_code, app_names in resource_mappings.items():
            group_resource = GroupResource.objects.filter(group=group_code).first()
            
            if group_resource:
                count = Resource.objects.filter(apps__in=app_names).update(
                    group_resource=group_resource
                )
                updated_count += count
                self.stdout.write(f'✓ Updated {count} resources for group: {group_code}')
            else:
                self.stdout.write(self.style.WARNING(f'! Group resource not found: {group_code}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Total resources updated: {updated_count}'))
