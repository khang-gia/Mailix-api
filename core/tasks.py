import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.db import transaction

logger = logging.getLogger('core')

@shared_task
def process_hard_delete_old_profiles():
    from core.models import ProfileHR
    
    logger.info('===================== Running permanent deletion of 30-day old soft-deleted profiles')
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    # Get profiles deleted more than 30 days ago
    # deleted_objects manager filters for is_deleted=True
    old_deleted_profiles = ProfileHR.deleted_objects.filter(deleted_at__lte=thirty_days_ago)
    
    count = 0
    for profile in old_deleted_profiles:
        try:
            with transaction.atomic():
                user = profile.user
                profile.hard_delete()  # permanently delete the profile
                if user:
                    user.delete()  # permanently delete the auth user
                count += 1
        except Exception as e:
            logger.error(f'Failed to permanently delete profile {profile.id}: {str(e)}')
            
    logger.info(f'===================== Successfully permanently deleted {count} profiles')
    return count
