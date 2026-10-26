from django.core.management.base import BaseCommand
from system.models import Department, BusinessUnit

class Command(BaseCommand):
    help = 'Initialize default departments structure'

    def handle(self, *args, **options):
        confirm = input('This will create default departments. Continue? [Y/n]: ')
        if confirm != 'Y':
            self.stdout.write('Cancelled')
            return
        
        # Create default business unit if not exists
        business_unit, _ = BusinessUnit.objects.get_or_create(
            name='Main Business Unit',
            defaults={'description': 'Default business unit'}
        )
        
        # Define default department structure
        departments = [
            {
                'code': 'HR',
                'name': 'Human Resources',
                'description': 'Human resources management',
                'department_type': 2
            },
            {
                'code': 'IT',
                'name': 'Information Technology',
                'description': 'IT and technical support',
                'department_type': 2
            },
            {
                'code': 'SALES',
                'name': 'Sales',
                'description': 'Sales and customer relations',
                'department_type': 2
            },
            {
                'code': 'FIN',
                'name': 'Finance',
                'description': 'Finance and accounting',
                'department_type': 2
            },
            {
                'code': 'OPS',
                'name': 'Operations',
                'description': 'Operations management',
                'department_type': 2
            },
        ]
        
        created_count = 0
        for dept_data in departments:
            obj, created = Department.objects.get_or_create(
                code=dept_data['code'],
                defaults={
                    'name': dept_data['name'],
                    'description': dept_data.get('description', ''),
                    'business_unit': business_unit,
                    'department_type': dept_data.get('department_type', 2)
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created: {dept_data["name"]} ({dept_data["code"]})'))
            else:
                self.stdout.write(f'Already exists: {dept_data["name"]} ({dept_data["code"]})')
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Successfully created {created_count} departments'))
