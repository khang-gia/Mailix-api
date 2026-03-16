from django.db import models
from django.dispatch.dispatcher import receiver
from django.db.models.signals import post_save
from core.mixins.base_model import BaseModel, BaseCreateDeleteModel, BaseCreateUpdateDeleteModel, BaseCreateUpdateModel
from simple_history.models import HistoricalRecords
# Create your models here.
class SocialGroup(BaseCreateUpdateDeleteModel):
    name = models.CharField(max_length=255)
    description = models.TextField()
    avatar = models.ImageField(upload_to='social_groups', null=True, blank=True)
    cover = models.ImageField(upload_to='social_groups', null=True, blank=True)
    is_public = models.BooleanField(default=True)
    #Company page informations
    slogan = models.CharField(max_length=255, null=True, blank=True)
    biography = models.TextField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    website = models.CharField(max_length=255, null=True, blank=True)
    established_date = models.DateField(null=True, blank=True)
    is_company = models.BooleanField(default=False)
    historical = HistoricalRecords()

    def __str__(self):
        return "SocialGroup {}".format(self.name)

GROUP_ROLES = (
    (1, 'Admin'),
    (2, 'Moderator'),
    (3, 'Anonym'),
    (4, 'Member'),
    (5, 'Representative')
)
GROUP_MEMBER_STATUSES = (
    (1, 'Active'),
    (2, 'Banned'),
    (3, 'Muted'),
    (4, 'Inactive')
)
class SocialGroupMember(BaseCreateUpdateDeleteModel):
    social_group = models.ForeignKey('SocialGroup', on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='social_group_members')
    role = models.IntegerField("Role", choices=GROUP_ROLES, default=4)
    status = models.IntegerField("Status", choices=GROUP_MEMBER_STATUSES, default=1)
    historical = HistoricalRecords()

POST_TYPES = (
    (1, 'Post'),
    (2, 'Poll'),
    (3, 'Announcement')
)
POST_STATUSES = (
    (1, 'Draft'),
    (2, 'Posting'),
    (3, 'Published'),
    (4, 'Deleted'),
    (5, 'Hidden'),
    (6, 'Pending'),
    (7, 'Denied')
)
class Post(BaseCreateUpdateDeleteModel):
    social_group = models.ForeignKey('SocialGroup', on_delete=models.SET_NULL, null=True, blank=True, related_name='posts', db_index=True)
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='posts', db_index=True)
    post_type = models.IntegerField("Type", choices=POST_TYPES, default=1)
    title = models.CharField("Title", max_length=255, null=True, blank=True)
    content = models.TextField("Content", null=True, blank=True)
    
    image = models.ImageField(upload_to='posts', null=True, blank=True)
    file = models.FileField(upload_to='posts', null=True, blank=True)
    is_pinned = models.BooleanField(default=False)
    allow_create_option = models.BooleanField(default=False)
    start_poll = models.DateTimeField(null=True, blank=True)
    end_poll = models.DateTimeField(null=True, blank=True)
    interactions_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    privacy = models.IntegerField("Privacy", choices=(
        (1, 'Public'),
        (2, 'Only Me')
    ), default=1)
    historical = HistoricalRecords()
    status = models.IntegerField("Status", choices=POST_STATUSES, default=1)

    def __str__(self):
        return "Post {}".format(self.title)
    
    def get_top_interaction_types(self, limit=3):
        """
        Get the top N most common interaction types for this post.
        Returns a list of dicts with interaction_type and count.
        Similar to Facebook's reaction summary (e.g., "👍 5  ❤️ 3  😂 2")
        """
        from django.db.models import Count
        
        top_interactions = (
            self.interactions
            .values('interaction_type')
            .annotate(count=Count('interaction_type'))
            .order_by('-count')[:limit]
        )
        
        return list(top_interactions)
class PollOption(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='poll_options')
    option = models.CharField("Option", max_length=255)
    votes_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "PollOption {}".format(self.pk)
INTERACTION_TYPES = (
    (1, 'Like'),
    (2, 'Dislike'),
    (3, 'Heart'),
    (4, 'Haha'),
    (5, 'Wow'),
    (6, 'Sad'),
    (7, 'Angry')
)
class PostInteraction(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='interactions')
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='post_interactions')
    interaction_type = models.IntegerField("Interaction Type", choices=INTERACTION_TYPES, default=1)
    created_at = models.DateTimeField('Created At', auto_now_add=True)
    updated_at = models.DateTimeField('Updated At', auto_now=True)

    def __str__(self):
        return "PostInteraction {}".format(self.pk)

    class Meta:
        unique_together = ('post', 'user')  
class PollVote(BaseCreateUpdateDeleteModel):
    # post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='poll_votes')
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='poll_votes')
    poll_option = models.ForeignKey('PollOption', on_delete=models.CASCADE, related_name='poll_votes')
    historical = HistoricalRecords()

    def __str__(self):
        return "PollVote {}".format(self.pk)

class PostComment(BaseCreateUpdateDeleteModel):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    text = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='comment_replies')
    likes = models.ManyToManyField('auth.User', related_name='user_like_comments', blank=True)
    def like_count(self):
        return self.likes.count()

    def __str__(self):
        return "PostComment <{}> by {}".format(self.post, self.user)

class PostCommentAttachment(models.Model):
    comment = models.OneToOneField(
        'PostComment', related_name='attachment', on_delete=models.CASCADE
    )
    file = models.FileField(upload_to='post_comment_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    filename = models.CharField(max_length=255, blank=True, null=True)
    file_type = models.CharField(max_length=50, blank=True, null=True)  # 'image' or 'file'
    
    def save(self, *args, **kwargs):
        if not self.filename and self.file:
            self.filename = self.file.name
        
        # Auto-detect file type based on extension
        if self.file and not self.file_type:
            ext = self.filename.split('.')[-1].lower() if self.filename else ''
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']:
                self.file_type = 'image'
            else:
                self.file_type = 'file'
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Attachment for Comment {self.comment.pk}: {self.filename or 'No Name'}"

@receiver(signal=post_save, sender=PostComment)
def count_post_comments(sender, instance, created, **kwargs):
    if created:
        post = instance.post
        post.comments_count = post.comments.count()
        post.save()

@receiver(signal=post_save, sender='auth.User')
def create_user_social_profile(sender, instance, created, **kwargs):
    """Auto-create UserSocialProfile and add to company groups when a new User account is created"""
    if created:
        UserSocialProfile.objects.create(user=instance)
        
        # Determine role: Admin if superuser, otherwise Member
        role = 1 if instance.is_superuser else 4
        
        # Auto-add new user as a member of all company SocialGroups
        company_groups = SocialGroup.objects.filter(is_company=True)
        for group in company_groups:
            SocialGroupMember.objects.get_or_create(
                social_group=group,
                user=instance,
                defaults={'role': role, 'status': 1}  # Admin (1) or Member (4), Active
            )

class PostAttachment(BaseCreateUpdateDeleteModel):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='post_attachments')
    file_type = models.CharField(max_length=50)  # 'image', 'video', 'document', 'pdf'
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField()  # in bytes
    order = models.IntegerField(default=0)  # for ordering attachments
    historical = HistoricalRecords()
    
    class Meta:
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"Attachment {self.file_name} for Post {self.post.id}"

PRIVACY_CHOICES = (
    (1, 'Public'),
    (2, 'Friends Only'),
    (3, 'Only Me')
)

class UserSocialProfile(BaseCreateUpdateDeleteModel):
    """Social profile for users - stores bio, cover photo, and other wall-specific information"""
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='social_profile')
    bio = models.TextField('Bio/About', blank=True, null=True)
    avatar = models.ImageField(upload_to='social_avatars/', blank=True, null=True)
    cover_photo = models.ImageField(upload_to='social_covers/', blank=True, null=True)
    location = models.CharField('Location', max_length=255, blank=True, null=True)
    education = models.TextField('Education', blank=True, null=True)
    website = models.URLField('Website', blank=True, null=True)
    
    # Privacy settings for profile fields
    bio_privacy = models.IntegerField('Bio Privacy', choices=PRIVACY_CHOICES, default=1)
    location_privacy = models.IntegerField('Location Privacy', choices=PRIVACY_CHOICES, default=1)
    education_privacy = models.IntegerField('Education Privacy', choices=PRIVACY_CHOICES, default=1)
    website_privacy = models.IntegerField('Website Privacy', choices=PRIVACY_CHOICES, default=1)
    
    historical = HistoricalRecords()
    
    def __str__(self):
        return f"Social Profile for {self.user.username}"
    
    class Meta:
        verbose_name = 'User Social Profile'
        verbose_name_plural = 'User Social Profiles'

class Friendship(BaseCreateUpdateDeleteModel):
    """Friendship relationship between users"""
    from_user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='friendships_sent')
    to_user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='friendships_received')
    status = models.IntegerField('Status', choices=(
        (1, 'Pending'),
        (2, 'Accepted'),
        (3, 'Rejected'),
        (4, 'Blocked')
    ), default=1)
    historical = HistoricalRecords()
    
    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username} ({self.get_status_display()})"
    
    class Meta:
        unique_together = ('from_user', 'to_user')
        verbose_name = 'Friendship'
        verbose_name_plural = 'Friendships'