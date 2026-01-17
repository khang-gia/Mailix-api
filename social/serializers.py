from rest_framework import serializers
from .models import SocialGroup, SocialGroupMember, Post, PollOption, PostInteraction, PollVote, PostComment, PostAttachment, PostCommentAttachment
from core.serializers import UserOtherViewSerializer, UserListSerializer


class PostAttachmentSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = PostAttachment
        fields = ['id', 'file', 'file_type', 'file_name', 'file_size', 'order', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_file(self, obj):
        request = self.context.get('request')
        if obj.file:
            file_url = obj.file.url
            if request is not None:
                return request.build_absolute_uri(file_url)
            return file_url
        return None


class SocialGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialGroup
        fields = '__all__'


class SocialGroupListSerializer(serializers.ModelSerializer):
    members_count = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField(read_only=True)
    cover = serializers.SerializerMethodField(read_only=True)
    your_role = serializers.SerializerMethodField()
    
    class Meta:
        model = SocialGroup
        fields = '__all__'
    
    def get_members_count(self, obj):
        return obj.members.filter(status=1).count()
    
    def get_posts_count(self, obj):
        return obj.posts.count()
    
    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.avatar:
            avatar_url = obj.avatar.url
            if request is not None:
                return request.build_absolute_uri(avatar_url)
            return avatar_url
        return None
    
    def get_cover(self, obj):
        request = self.context.get('request')
        if obj.cover:
            cover_url = obj.cover.url
            if request is not None:
                return request.build_absolute_uri(cover_url)
            return cover_url
        return None
    
    def get_your_role(self, obj):
        """Get the current user's role in this group, if they are a member"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            membership = obj.members.filter(user=request.user, status=1).first()
            if membership:
                return membership.get_role_display()
        return None


class SocialGroupDetailSerializer(serializers.ModelSerializer):
    members_count = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField(read_only=True)
    cover = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = SocialGroup
        fields = '__all__'
    
    def get_members_count(self, obj):
        return obj.members.filter(status=1).count()
    
    def get_posts_count(self, obj):
        return obj.posts.count()
    
    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.avatar:
            avatar_url = obj.avatar.url
            if request is not None:
                return request.build_absolute_uri(avatar_url)
            return avatar_url
        return None
    
    def get_cover(self, obj):
        request = self.context.get('request')
        if obj.cover:
            cover_url = obj.cover.url
            if request is not None:
                return request.build_absolute_uri(cover_url)
            return cover_url
        return None


class SocialGroupMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialGroupMember
        fields = '__all__'


class SocialGroupMemberListSerializer(serializers.ModelSerializer):
    user = UserOtherViewSerializer(read_only=True)
    social_group_name = serializers.CharField(source='social_group.name', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = SocialGroupMember
        fields = '__all__'


class PollVoteUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollVote
        fields = ['user']
        
class PollOptionSerializer(serializers.ModelSerializer):
    # poll_votes = PollVoteUserSerializer(many=True, read_only=True)
    poll_vote_users = serializers.SerializerMethodField()
    
    class Meta:
        model = PollOption
        fields = '__all__'

    def get_poll_vote_users(self, obj):
        return obj.poll_votes.values_list('user', flat=True)
class PollOptionsGeneralSerializer(serializers.ModelSerializer):
    votes_count = serializers.IntegerField(read_only=True)
    has_voted = serializers.SerializerMethodField()
    
    class Meta:
        model = PollOption
        fields = '__all__'
    
    def get_has_voted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.poll_votes.filter(user=request.user).exists()
        return False
class PollVoteUserOnlySerializer(serializers.ModelSerializer):
    """Serializer for poll votes with only user information (no poll option details)"""
    user = UserOtherViewSerializer(read_only=True)
    
    class Meta:
        model = PollVote
        fields = ['id', 'user', 'created_at']


class PollOptionDetailSerializer(serializers.ModelSerializer):
    poll_votes = PollVoteUserOnlySerializer(many=True, read_only=True)
    votes_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = PollOption
        fields = '__all__'

    # def get_poll_votes(self, obj):
    #     # Return poll votes with only user information (no circular poll option reference)
    #     return PollVoteUserOnlySerializer(obj.poll_votes.all(), many=True, context=self.context).data

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

class PostCreateSerializer(serializers.ModelSerializer):
    poll_options = serializers.ListField(
        child=serializers.CharField(max_length=255),
        write_only=True,
        required=False,
        allow_empty=False
    )
    
    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = ['author']
    
    def create(self, validated_data):
        from .tasks import process_post_creation
        
        # Extract poll_options if present
        poll_options_data = validated_data.pop('poll_options', None)
        
        # Set initial status to 'Posting' (2) if not explicitly set
        if 'status' not in validated_data:
            validated_data['status'] = 2  # Posting
        
        # Create the post with 'Posting' status
        post = Post.objects.create(**validated_data)
        
        # Trigger async task to process post creation
        # This will create poll options and update status to 'Published'
        process_post_creation.delay(
            post_id=post.id,
            poll_options=poll_options_data
        )
        
        return post

class PostListSerializer(serializers.ModelSerializer):
    author = UserOtherViewSerializer(read_only=True)
    social_group_name = serializers.CharField(source='social_group.name', read_only=True)
    post_type_display = serializers.CharField(source='get_post_type_display', read_only=True)
    image = serializers.SerializerMethodField(read_only=True)
    file = serializers.SerializerMethodField(read_only=True)
    poll_options = PollOptionSerializer(many=True, read_only=True)
    your_interaction = serializers.SerializerMethodField()
    top_interaction_types = serializers.SerializerMethodField()
    attachments = PostAttachmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Post
        fields = '__all__'
    
    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            image_url = obj.image.url
            if request is not None:
                return request.build_absolute_uri(image_url)
            return image_url
        return None
    
    def get_file(self, obj):
        request = self.context.get('request')
        if obj.file:
            file_url = obj.file.url
            if request is not None:
                return request.build_absolute_uri(file_url)
            return file_url
        return None
    
    def get_your_interaction(self, obj):
        """Get the user's interaction type if they have interacted, otherwise None"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            interaction = obj.interactions.filter(user=request.user).first()
            if interaction:
                return interaction.interaction_type
        return None
    
    def get_top_interaction_types(self, obj):
        """Get top 3 interaction types for this post"""
        return obj.get_top_interaction_types(limit=3)

class PostDetailSerializer(serializers.ModelSerializer):
    author = UserOtherViewSerializer(read_only=True)
    social_group = SocialGroupListSerializer(read_only=True)
    post_type_display = serializers.CharField(source='get_post_type_display', read_only=True)
    poll_options = PollOptionsGeneralSerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField(read_only=True)
    file = serializers.SerializerMethodField(read_only=True)
    user_interaction = serializers.SerializerMethodField()
    attachments = PostAttachmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Post
        fields = '__all__'
    
    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            image_url = obj.image.url
            if request is not None:
                return request.build_absolute_uri(image_url)
            return image_url
        return None
    
    def get_file(self, obj):
        request = self.context.get('request')
        if obj.file:
            file_url = obj.file.url
            if request is not None:
                return request.build_absolute_uri(file_url)
            return file_url
        return None
    
    def get_user_interaction(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            interaction = obj.interactions.filter(user=request.user).first()
            if interaction:
                return {
                    'interaction_type': interaction.interaction_type,
                    'interaction_type_display': interaction.get_interaction_type_display()
                }
        return None


class PostInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostInteraction
        fields = '__all__'


class PostInteractionListSerializer(serializers.ModelSerializer):
    user = UserOtherViewSerializer(read_only=True)
    interaction_type_display = serializers.CharField(source='get_interaction_type_display', read_only=True)
    
    class Meta:
        model = PostInteraction
        fields = '__all__'


class PollVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollVote
        fields = '__all__'


class PollVoteListSerializer(serializers.ModelSerializer):
    user = UserOtherViewSerializer(read_only=True)
    poll_option_text = serializers.CharField(source='poll_option.option', read_only=True)
    
    class Meta:
        model = PollVote
        fields = '__all__'

class PostCommentAttachmentSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()
    
    class Meta:
        model = PostCommentAttachment
        fields = ['id', 'file', 'filename', 'file_type', 'uploaded_at']
    
    def get_file(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url if obj.file else None

class PostCommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    likes = UserListSerializer(read_only=True, many=True)
    like_count = serializers.SerializerMethodField()
    is_liked_by_you = serializers.SerializerMethodField()
    attachment = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PostComment
        fields = '__all__'
    
    def get_user(self, obj):
      user_serializer = UserOtherViewSerializer(obj.user, context=self.context)
      return user_serializer.data

    def get_like_count(self, obj):
        return obj.like_count()

    def get_is_liked_by_you(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False
    
    def get_attachment(self, obj):
        try:
            if hasattr(obj, 'attachment') and obj.attachment:
                return PostCommentAttachmentSerializer(obj.attachment, context=self.context).data
        except PostCommentAttachment.DoesNotExist:
            pass
        return None
    
    def get_replies(self, obj):
        """Get replies only for top-level comments (1-level nesting only)"""
        if obj.parent is None:
            # Only serialize replies for top-level comments
            replies = obj.comment_replies.filter(deleted_at__isnull=True).order_by('created_at')
            # Use the same serializer but replies won't have nested replies (parent != None)
            return PostCommentSerializer(replies, many=True, context=self.context).data
        return []
    
    def get_reply_count(self, obj):
        """Get reply count only for top-level comments"""
        if obj.parent is None:
            return obj.comment_replies.filter(deleted_at__isnull=True).count()
        return 0


class PostCommentCreateSerializer(serializers.ModelSerializer):
  
  attachment = serializers.FileField(required=False, write_only=True)
  text = serializers.CharField(required=False, allow_blank=True)
  
  class Meta:
        model = PostComment
        exclude = ['likes',]
  
  def validate(self, data):
      # Ensure at least one of text or attachment is provided
      if not data.get('text') and not data.get('attachment'):
          raise serializers.ValidationError("Either text or attachment must be provided.")
      return data
  
  def create(self, validated_data):
      # Extract attachment file if present
      attachment_file = validated_data.pop('attachment', None)
      
      # Create the comment
      comment = PostComment.objects.create(**validated_data)
      
      # Create attachment if file was provided
      if attachment_file:
          PostCommentAttachment.objects.create(
              comment=comment,
              file=attachment_file
          )
      
      return comment