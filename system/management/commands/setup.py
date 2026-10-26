from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = (
        'Run the full system setup in one command:\n'
        '  1. migrate\n'
        '  2. init_group_resource   (resource categories)\n'
        '  3. init_resource         (API resources)\n'
        '  4. init_groups           (Admin / Manager / User system groups)\n'
        '  5. init_system_resources (SystemResource + ADM group)\n'
        '  6. init_departments      (default departments)\n'
        '  7. init_permission       (create all group×resource permission rows)\n'
        '  8. set_permission        (apply default allow/deny rules)\n'
        '  9. set_group_resource    (link resources → categories)\n'
        ' 10. set_company_modules   (enable default modules on companies)\n'
        ' 11. create_user_profiles  (social profiles + company group sync)\n'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-migrate',
            action='store_true',
            default=False,
            help='Skip running migrations (useful if DB is already up to date)',
        )
        parser.add_argument(
            '--skip-seed',
            action='store_true',
            default=False,
            help='Skip creating social profiles / company group sync',
        )
        parser.add_argument(
            '--no-input',
            action='store_true',
            default=False,
            help='Skip all confirmation prompts (non-interactive mode)',
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _step(self, number, label):
        self.stdout.write(
            self.style.HTTP_INFO(f'\n[{number}] {label}')
        )
        self.stdout.write(self.style.HTTP_INFO('─' * 50))

    def _ok(self, msg='Done'):
        self.stdout.write(self.style.SUCCESS(f'    ✓ {msg}'))

    def _skip_confirm(self, prompt):
        """Return True (proceed) always when --no-input, else ask the user."""
        if self._no_input:
            return True
        answer = input(f'{prompt} [Y/n]: ')
        return answer.strip().upper() in ('Y', '')

    # ------------------------------------------------------------------
    # Patched sub-commands that need a confirmation prompt
    # ------------------------------------------------------------------

    def _run_init_departments(self):
        """init_departments asks for confirmation; replicate its logic inline."""
        from system.models import Department, BusinessUnit

        departments = [
            {'code': 'HR',   'name': 'Human Resources',        'description': 'Human resources management',   'department_type': 2},
            {'code': 'IT',   'name': 'Information Technology',  'description': 'IT and technical support',      'department_type': 2},
            {'code': 'SALES','name': 'Sales',                   'description': 'Sales and customer relations',  'department_type': 2},
            {'code': 'FIN',  'name': 'Finance',                 'description': 'Finance and accounting',        'department_type': 2},
            {'code': 'OPS',  'name': 'Operations',              'description': 'Operations management',         'department_type': 2},
        ]

        business_unit, _ = BusinessUnit.objects.get_or_create(
            name='Main Business Unit',
            defaults={'description': 'Default business unit'},
        )

        created_count = 0
        for dept_data in departments:
            obj, created = Department.objects.get_or_create(
                code=dept_data['code'],
                defaults={
                    'name': dept_data['name'],
                    'description': dept_data.get('description', ''),
                    'business_unit': business_unit,
                    'department_type': dept_data.get('department_type', 2),
                },
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(
                    f'    ✓ Created: {dept_data["name"]} ({dept_data["code"]})'
                ))
            else:
                self.stdout.write(f'    · Already exists: {dept_data["name"]} ({dept_data["code"]})')

        self.stdout.write(self.style.SUCCESS(f'    ✓ {created_count} departments created'))

    def _run_init_permission(self):
        """init_permission asks for confirmation; replicate its logic inline."""
        from system.models import Resource, Permission, SystemGroup

        resources = Resource.objects.all()
        groups = SystemGroup.objects.all()

        if not resources.exists():
            self.stdout.write(self.style.ERROR('    ✗ No resources found – run init_resource first'))
            return
        if not groups.exists():
            self.stdout.write(self.style.ERROR('    ✗ No groups found – run init_groups first'))
            return

        created_count = 0
        total = 0
        for resource in resources:
            for group in groups:
                _, created = Permission.objects.get_or_create(
                    resource=resource,
                    group=group,
                    defaults={'status': False},
                )
                if created:
                    created_count += 1
                total += 1

        self.stdout.write(self.style.SUCCESS(
            f'    ✓ {created_count} new permission rows created (total: {total})'
        ))

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def handle(self, *args, **options):
        self._no_input = options['no_input']

        self.stdout.write(self.style.SUCCESS('\n' + '=' * 50))
        self.stdout.write(self.style.SUCCESS(' MAILIX — FULL SYSTEM SETUP'))
        self.stdout.write(self.style.SUCCESS('=' * 50))

        # ── Step 1: Migrate ──────────────────────────────────────────
        if not options['skip_migrate']:
            self._step(1, 'Running database migrations')
            call_command('migrate', '--no-input' if self._no_input else '--run-syncdb')
            self._ok('Migrations applied')
        else:
            self.stdout.write(self.style.WARNING('\n[1] Skipping migrations (--skip-migrate)'))

        # ── Step 2: init_group_resource ───────────────────────────────
        self._step(2, 'Initializing resource categories (GroupResource)')
        call_command('init_group_resource')
        self._ok()

        # ── Step 3: init_resource ────────────────────────────────────
        self._step(3, 'Initializing API resources (Resource)')
        call_command('init_resource')
        self._ok()

        # ── Step 4: init_groups ──────────────────────────────────────
        self._step(4, 'Initializing system groups (Admin / Manager / User)')
        call_command('init_groups')
        self._ok()

        # ── Step 5: init_system_resources ────────────────────────────
        self._step(5, 'Initializing system resources + ADM group')
        call_command('init_system_resources')
        self._ok()

        # ── Step 6: init_departments ─────────────────────────────────
        self._step(6, 'Initializing default departments')
        self._run_init_departments()

        # ── Step 7: init_permission ──────────────────────────────────
        self._step(7, 'Creating permission matrix (all groups × resources)')
        self._run_init_permission()

        # ── Step 8: set_permission ───────────────────────────────────
        self._step(8, 'Applying default permission rules')
        call_command('set_permission')
        self._ok()

        # ── Step 9: set_group_resource ───────────────────────────────
        self._step(9, 'Linking resources to their categories')
        call_command('set_group_resource')
        self._ok()

        # ── Step 10: set_company_modules ─────────────────────────────
        self._step(10, 'Setting default company modules')
        call_command('set_company_modules')
        self._ok()

        # ── Step 11: create_user_profiles ────────────────────────────
        if not options['skip_seed']:
            self._step(11, 'Creating social profiles + syncing company group')
            call_command('create_user_profiles')
            self._ok()
        else:
            self.stdout.write(self.style.WARNING('\n[11] Skipping social profile sync (--skip-seed)'))

        # ── Done ─────────────────────────────────────────────────────
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 50))
        self.stdout.write(self.style.SUCCESS(' ✓ SETUP COMPLETE'))
        self.stdout.write(self.style.SUCCESS('=' * 50 + '\n'))
