from django.core.management.base import BaseCommand
from system.models import Company

class Command(BaseCommand):
    help = 'Set default modules for companies'

    def add_arguments(self, parser):
        parser.add_argument(
            '--modules',
            nargs='+',
            default=['crm', 'hrm', 'inventory'],
            help='List of default modules to enable (default: crm hrm inventory)'
        )
        parser.add_argument(
            '--company-id',
            type=int,
            help='Set modules for a specific company ID'
        )

    def handle(self, *args, **options):
        default_modules = options['modules']
        company_id = options.get('company_id')
        
        if company_id:
            # Set modules for a specific company
            try:
                company = Company.objects.get(id=company_id)
                company.enabled_modules = default_modules
                company.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Set modules for {company.name}: {default_modules}'
                    )
                )
            except Company.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Company with ID {company_id} not found')
                )
        else:
            # Set default modules for all companies
            updated_count = 0
            for company in Company.objects.all():
                if not company.enabled_modules:
                    company.enabled_modules = default_modules
                    company.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Set modules for {company.name}: {default_modules}'
                        )
                    )
                    updated_count += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Skipped {company.name} (already has modules: {company.enabled_modules})'
                        )
                    )
            
            self.stdout.write(
                self.style.SUCCESS(f'\nDONE. Updated {updated_count} companies.')
            )
