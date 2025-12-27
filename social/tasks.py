from celery import shared_task
from django.utils import timezone
import logging
import time

logger = logging.getLogger('app')


@shared_task
def process_post_creation(post_id, poll_options=None, delay_seconds=0):
    """
    Process post creation asynchronously.
    This task handles:
    - Creating poll options if the post is a poll
    - Updating post status from 'Posting' to 'Published'
    - Any future post-creation processing (notifications, indexing, etc.)
    
    Args:
        post_id: ID of the post to process
        poll_options: List of poll option texts (for poll type posts)
        delay_seconds: Simulated processing time in seconds (default: 5)
    """
    from .models import Post, PollOption
    
    logger.info(f'[Celery] process_post_creation for post_id: {post_id}')
    
    # Simulate complex processing time (for testing)
    if delay_seconds > 0:
        logger.info(f'Simulating {delay_seconds}s processing time for post {post_id}')
        time.sleep(delay_seconds)
    
    try:
        post = Post.objects.get(id=post_id)
        
        # Create poll options if this is a poll
        if post.post_type == 2 and poll_options:
            for option_text in poll_options:
                PollOption.objects.create(
                    post=post,
                    option=option_text,
                    votes_count=0
                )
            logger.info(f'Created {len(poll_options)} poll options for post {post_id}')
        
        # Update status from 'Posting' (2) to 'Published' (3)
        if post.status == 2:  # Posting
            post.status = 3  # Published
            post.save(update_fields=['status'])
            logger.info(f'Post {post_id} status updated to Published')
        
        # Future: Add more post-processing here
        # - Send notifications to group members
        # - Index post for search
        # - Generate thumbnails for images
        # - etc.
        
        return {
            'success': True,
            'post_id': post_id,
            'status': 'published'
        }
        
    except Post.DoesNotExist:
        logger.error(f'Post {post_id} not found')
        return {
            'success': False,
            'error': 'Post not found'
        }
    except Exception as e:
        logger.error(f'Error processing post {post_id}: {str(e)}')
        # Update post status to indicate error
        try:
            post = Post.objects.get(id=post_id)
            post.status = 1  # Back to Draft
            post.save(update_fields=['status'])
        except:
            pass
        raise
