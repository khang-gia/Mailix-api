from django.core.management.base import BaseCommand
from system.models import GroupResource

class Command(BaseCommand):
    help = 'Initialize resource categories'
    
    def handle(self, *args, **options):
        groups = [
            ('hr', 'Human Resources'),
            ('customer', 'Customer Management'),
            ('social', 'Social Features'),
            ('email', 'Email Management'),
            ('timekeeping', 'Time Tracking'),
            ('consult', 'Consultation'),
            ('system', 'System Management'),
            ('analytics', 'Analytics & Reports'),
            ('work', 'Work Management'),
        ]
        
        created_count = 0
        for code, name in groups:
            obj, created = GroupResource.objects.get_or_create(
                group=code,
                defaults={'name': name}
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created: {name} ({code})'))
            else:
                self.stdout.write(f'Already exists: {name} ({code})')
        
        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully created {created_count} group resources'))
