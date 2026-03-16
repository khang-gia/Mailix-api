from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from social.models import UserSocialProfile, SocialGroup, SocialGroupMember


class Command(BaseCommand):
    help = 'Create UserSocialProfile for all users who do not have one, and sync all users into the company group'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating profiles',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        company_group = SocialGroup.objects.filter(is_company=True).first()
        
        # Get all users who don't have a social profile
        users_without_profile = User.objects.filter(social_profile__isnull=True)
        total_users = users_without_profile.count()
        
        if total_users == 0:
            self.stdout.write(self.style.SUCCESS('All users already have social profiles!'))
            self.stdout.write('Checking company group memberships for all users...')
            self._sync_company_members(User.objects.all(), company_group, dry_run)
            return
        
        if dry_run:
            self.stdout.write(self.style.WARNING(f'DRY RUN: Would create {total_users} social profiles'))
            self.stdout.write('Users without profiles:')
            for user in users_without_profile:
                self.stdout.write(f'  - {user.username} (ID: {user.id})')
            return
        
        # Create profiles for users who don't have one
        created_count = 0
        for user in users_without_profile:
            try:
                UserSocialProfile.objects.create(user=user)
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created profile for {user.username} (ID: {user.id})')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to create profile for {user.username}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully created {created_count} out of {total_users} social profiles')
        )
        
        # Sync ALL users into the company group
        self.stdout.write('Syncing all users into the company group...')
        self._sync_company_members(User.objects.all(), company_group, dry_run)

    def _sync_company_members(self, users, company_group, dry_run=False):
        """Ensure every user is a member of the company group. Creates the group if it doesn't exist."""
        if not company_group:
            if dry_run:
                self.stdout.write(self.style.WARNING('No company group found. [DRY RUN] Would create one.'))
                return
            self.stdout.write(self.style.WARNING('No company group found. Creating one...'))
            company_group = SocialGroup.objects.create(
                name='Company',
                description='Official internal company social group.',
                is_public=True,
                is_company=True,
            )
            self.stdout.write(self.style.SUCCESS(f'Created company group: "{company_group.name}"'))
        
        added_count = 0
        for user in users:
            if dry_run:
                if not SocialGroupMember.objects.filter(social_group=company_group, user=user).exists():
                    self.stdout.write(f'  [DRY RUN] Would add {user.username} to "{company_group.name}"')
                continue
            _, created = SocialGroupMember.objects.get_or_create(
                social_group=company_group,
                user=user,
                defaults={'role': 1 if user.is_superuser else 4, 'status': 1}  # Admin (1) or Member (4), Active
            )
            if created:
                added_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'  Added {user.username} to "{company_group.name}"')
                )
        
        if not dry_run:
            self.stdout.write(self.style.SUCCESS(f'Sync complete. Added {added_count} new members.'))
