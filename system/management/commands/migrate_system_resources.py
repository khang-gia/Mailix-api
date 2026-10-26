from django.core.management.base import BaseCommand
from system.models import SystemResource, SystemGroup


class Command(BaseCommand):
    help = (
        'Migrates SystemResource codes to align with enabled_modules naming. '
        'Run once on deploy after the RBAC + view-lock integration. '
        'Idempotent: safe to run multiple times.'
    )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting SystemResource migration...'))

        # ------------------------------------------------------------------
        # 1. Rename 'customer' → 'hrm'
        #    (Nhân sự HR category must match enabled_modules key 'hrm')
        # ------------------------------------------------------------------
        updated = SystemResource.objects.filter(code='customer').update(code='hrm')
        if updated:
            self.stdout.write(self.style.SUCCESS(f'  ✓ Renamed customer → hrm ({updated} record(s))'))
        else:
            self.stdout.write(self.style.WARNING('  ⟳ customer → hrm: already renamed or not found'))

        # ------------------------------------------------------------------
        # 2. Rename 'guide' → 'guide_mail'
        #    (split into mail guide and app guide)
        # ------------------------------------------------------------------
        updated = SystemResource.objects.filter(code='guide').update(
            code='guide_mail',
            name='Hướng dẫn Mail',
            apps='mail',
        )
        if updated:
            self.stdout.write(self.style.SUCCESS(f'  ✓ Renamed guide → guide_mail ({updated} record(s))'))
        else:
            self.stdout.write(self.style.WARNING('  ⟳ guide → guide_mail: already renamed or not found'))

        # ------------------------------------------------------------------
        # 3. Create 'guide_app' if it does not exist yet
        # ------------------------------------------------------------------
        obj, created = SystemResource.objects.get_or_create(
            code='guide_app',
            defaults={
                'name': 'Hướng dẫn App',
                'apps': 'app',
                'description': 'App guide and documentation',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('  ✓ Created guide_app SystemResource'))

            # Also add guide_app to every group that already has guide_mail,
            # so existing departments keep consistent access.
            guide_mail = SystemResource.objects.filter(code='guide_mail').first()
            if guide_mail:
                for group in SystemGroup.objects.filter(resources=guide_mail):
                    group.resources.add(obj)
                    self.stdout.write(f'    → Added guide_app to group: {group.name}')
        else:
            self.stdout.write(self.style.WARNING('  ⟳ guide_app already exists, skipped'))

        # ------------------------------------------------------------------
        # 4. 'task' — intentionally left as-is (unused)
        # ------------------------------------------------------------------
        self.stdout.write('  ⏭  task: unused, left unchanged')

        # ------------------------------------------------------------------
        # Summary
        # ------------------------------------------------------------------
        self.stdout.write(self.style.SUCCESS('\nMigration complete. Current SystemResources:'))
        for r in SystemResource.objects.all().order_by('code'):
            self.stdout.write(f'  {r.code:15} | {r.name}')
