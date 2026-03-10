from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from social.models import UserSocialProfile


class Command(BaseCommand):
    help = 'Create UserSocialProfile for all users who do not have one'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating profiles',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Get all users who don't have a social profile
        users_without_profile = User.objects.filter(social_profile__isnull=True)
        
        total_users = users_without_profile.count()
        
        if total_users == 0:
            self.stdout.write(self.style.SUCCESS('All users already have social profiles!'))
            return
        
        if dry_run:
            self.stdout.write(self.style.WARNING(f'DRY RUN: Would create {total_users} social profiles'))
            self.stdout.write('Users without profiles:')
            for user in users_without_profile:
                self.stdout.write(f'  - {user.username} (ID: {user.id})')
            return
        
        # Create profiles
        created_count = 0
        from social.models import SocialGroup, SocialGroupMember
        company_groups = SocialGroup.objects.filter(is_company=True)

        for user in users_without_profile:
            try:
                UserSocialProfile.objects.create(user=user)
                # Also add to company groups
                for group in company_groups:
                    SocialGroupMember.objects.get_or_create(
                        social_group=group,
                        user=user,
                        defaults={'role': 4, 'status': 1}  # Member, Active
                    )
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
