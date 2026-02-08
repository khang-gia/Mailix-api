from django.shortcuts import render
from rest_framework import viewsets, status, parsers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import FilterSet
import django_filters
from django.db.models import Q, F, Count
from django.utils import timezone


from .models import SocialGroup, SocialGroupMember, Post, PollOption, PostInteraction, PollVote, PostComment, UserSocialProfile, Friendship
from .serializers import (
    SocialGroupSerializer, SocialGroupListSerializer, SocialGroupDetailSerializer,
    SocialGroupMemberSerializer, SocialGroupMemberListSerializer,
    PostSerializer, PostListSerializer, PostDetailSerializer, PostCreateSerializer,
    PollOptionSerializer, PollOptionDetailSerializer,
    PostInteractionSerializer, PostInteractionListSerializer,
    PollVoteSerializer, PollVoteListSerializer, PostCommentSerializer, PostCommentCreateSerializer,
    UserSocialProfileSerializer, FriendshipSerializer
)


class SocialGroupFilter(FilterSet):
    search = django_filters.CharFilter(method='elastic_search')
    my_groups = django_filters.BooleanFilter(method='filter_my_groups')
    
    class Meta:
        model = SocialGroup
        fields = ['name', 'is_public', 'is_company']
    
    def elastic_search(self, queryset, name, value):
        if not value:
            return queryset
        fields = ['name__icontains', 'description__icontains']
        _q = Q()
        for field in fields:
            _q = _q | Q(**{field: value})
        return queryset.filter(_q)
    
    def filter_my_groups(self, queryset, name, value):
        """Filter to show only groups where the user is a member"""
        if not value:
            return queryset
        
        user = self.request.user
        # Get group IDs where user is a member
        user_group_ids = SocialGroupMember.objects.filter(
            user=user,
            status=1  # Active members only
        ).values_list('social_group_id', flat=True)
        
        return queryset.filter(id__in=user_group_ids)


class SocialGroupViewSet(viewsets.ModelViewSet):
    queryset = SocialGroup.objects.all()
    serializer_class = SocialGroupSerializer
    filterset_class = SocialGroupFilter
    permission_classes = [IsAuthenticated]
    ordering_fields = ['id', 'created_at', 'name', 'membership_date']
    ordering = ('-id',)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SocialGroupListSerializer
        elif self.action == 'retrieve':
            return SocialGroupDetailSerializer
        return SocialGroupSerializer
    
    def get_queryset(self):
        """
        Return groups that the user can access:
        - All public groups
        - Private groups where the user is a member
        - All groups if user is superuser
        """
        if self.request.user.is_superuser:
            return SocialGroup.objects.all()
        
        user = self.request.user
        
        # Get IDs of groups where user is a member
        user_group_ids = SocialGroupMember.objects.filter(
            user=user,
            status=1  # Active members only
        ).values_list('social_group_id', flat=True)
        
        # Return public groups OR groups where user is a member
        return SocialGroup.objects.filter(
            Q(is_public=True) | Q(id__in=user_group_ids)
        ).distinct()
    
    def filter_queryset(self, queryset):
        """
        Apply filters and handle membership_date annotation for sorting
        """
        # Check if we need to annotate with membership_date
        my_groups_filter = self.request.query_params.get('my_groups')
        ordering = self.request.query_params.get('ordering', '')
        
        if my_groups_filter and 'membership_date' in ordering:
            from django.db.models import Subquery, OuterRef
            
            user = self.request.user
            
            # Subquery to get the membership created_at for each group
            membership_subquery = SocialGroupMember.objects.filter(
                social_group=OuterRef('pk'),
                user=user,
                status=1
            ).values('created_at')[:1]
            
            queryset = queryset.annotate(
                membership_date=Subquery(membership_subquery)
            )
        
        # Apply the rest of the filters (including ordering)
        return super().filter_queryset(queryset)

    def perform_create(self, serializer):
        """Create group and automatically add creator as admin member"""
        group = serializer.save()
        
        # Automatically create membership for the creator as Admin
        SocialGroupMember.objects.create(
            social_group=group,
            user=self.request.user,
            role=1,  # Admin role
            status=1  # Active status
        )
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get all members of a social group"""
        group = self.get_object()
        members = group.members.all().order_by('-created_at')
        serializer = SocialGroupMemberListSerializer(members, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join a social group"""
        group = self.get_object()
        user = request.user
        
        # Check if user is already a member
        if group.members.filter(user=user).exists():
            return Response({'detail': 'You are already a member of this group.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create membership
        member = SocialGroupMember.objects.create(
            social_group=group,
            user=user,
            role=4,  # Member role
            status=1  # Active status
        )
        
        serializer = SocialGroupMemberListSerializer(member, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Leave a social group"""
        group = self.get_object()
        user = request.user
        
        try:
            member = group.members.get(user=user)
            member.delete()
            return Response({'detail': 'You have left the group.'}, status=status.HTTP_200_OK)
        except SocialGroupMember.DoesNotExist:
            return Response({'detail': 'You are not a member of this group.'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def add_members(self, request, pk=None):
        """Add multiple members to a group (admin only)"""
        group = self.get_object()
        
        # Check if user is admin of the group
        if not group.members.filter(user=request.user, role=1, status=1).exists() and not request.user.is_superuser:
             return Response({'detail': 'Only group admins can add members.'}, status=status.HTTP_403_FORBIDDEN)

        user_ids = request.data.get('user_ids', [])
        if not user_ids:
            return Response({'detail': 'No users selected.'}, status=status.HTTP_400_BAD_REQUEST)

        added_count = 0
        for user_id in user_ids:
            # Check if already member
            if not group.members.filter(user_id=user_id).exists():
                try:
                    SocialGroupMember.objects.create(
                        social_group=group,
                        user_id=user_id,
                        role=4, # Member
                        status=1 # Active
                    )
                    added_count += 1
                except Exception as e:
                    pass
        
        return Response({'detail': f'Added {added_count} members.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        """Get all posts in a social group"""
        from django.db.models import Case, When, IntegerField
        
        group = self.get_object()
        posts = group.posts.filter(status=3).select_related('author').annotate(
            # Create a sort priority: pinned announcements = 0, regular posts = 1
            sort_priority=Case(
                When(is_pinned=True, post_type=3, then=0),  # Pinned announcements first
                default=1,
                output_field=IntegerField()
            )
        ).order_by('sort_priority', '-is_pinned', '-created_at')
        
        serializer = PostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def importants(self, request, pk=None):
        """
        Get all important posts (announcements) for this group.
        Returns posts with post_type=3 (Announcement) for the specified group.
        """
        group = self.get_object()
        
        # Get announcement posts for this group, ordered by creation date
        important_posts = Post.objects.filter(
            social_group=group,
            post_type=3,  # Announcement type
            status=3,  # Published status
            deleted_at__isnull=True
        ).select_related('author').order_by('-is_pinned', '-created_at')
        
        serializer = PostListSerializer(important_posts, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)



class SocialGroupMemberFilter(FilterSet):
    social_group = django_filters.NumberFilter(field_name='social_group__id')
    user = django_filters.NumberFilter(field_name='user__id')
    
    class Meta:
        model = SocialGroupMember
        fields = ['social_group', 'user', 'role', 'status']


class SocialGroupMemberViewSet(viewsets.ModelViewSet):
    queryset = SocialGroupMember.objects.all()
    serializer_class = SocialGroupMemberSerializer
    filterset_class = SocialGroupMemberFilter
    permission_classes = [IsAuthenticated]
    ordering_fields = ['id', 'created_at']
    ordering = ('-id',)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SocialGroupMemberListSerializer
        return SocialGroupMemberSerializer
    
    @action(detail=True, methods=['post'])
    def change_role(self, request, pk=None):
        """Change member role (admin/moderator only)"""
        member = self.get_object()
        new_role = request.data.get('role')
        
        if not new_role:
            return Response({'detail': 'Role is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        member.role = new_role
        member.save()
        
        serializer = SocialGroupMemberListSerializer(member, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """Change member status (admin/moderator only)"""
        member = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response({'detail': 'Status is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        member.status = new_status
        member.save()
        
        serializer = SocialGroupMemberListSerializer(member, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class PostFilter(FilterSet):
    search = django_filters.CharFilter(method='elastic_search')
    social_group = django_filters.NumberFilter(field_name='social_group__id')
    author = django_filters.NumberFilter(field_name='author__id')
    post_types = django_filters.CharFilter(method='filter_post_types')
    new_feed = django_filters.BooleanFilter(method='filter_new_feed')
    
    class Meta:
        model = Post
        fields = ['social_group', 'author', 'post_type', 'is_pinned', 'status']
    
    def filter_new_feed(self, queryset, name, value):
        if not value:
            return queryset
        
        user = self.request.user
        # Get IDs of groups where user is a member
        user_group_ids = SocialGroupMember.objects.filter(
            user=user,
            status=1  # Active members only
        ).values_list('social_group_id', flat=True)
        return queryset.filter(
            Q(author=user) | 
            (
                Q(privacy=1) & 
                (
                    Q(social_group__isnull=True) | 
                    Q(social_group__in=user_group_ids) |
                    Q(social_group__is_company=True)
                )
            )
        )
    
    def elastic_search(self, queryset, name, value):
        if not value:
            return queryset
        fields = ['title__icontains', 'content__icontains']
        _q = Q()
        for field in fields:
            _q = _q | Q(**{field: value})
        return queryset.filter(_q)
    
    def filter_post_types(self, queryset, name, value):
        if not value:
            return queryset
        post_type_ids = value.split(',')
        return queryset.filter(post_type__in=post_type_ids).distinct()


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filterset_class = PostFilter
    permission_classes = [IsAuthenticated]
    ordering_fields = ['id', 'created_at', 'interactions_count', 'comments_count']
    ordering = ('-created_at',)
    
    def get_queryset(self):
        """Filter posts based on user's group memberships"""
        queryset = super().get_queryset()
        # You can add logic here to filter posts from groups the user is a member of
        # Filter posts basesd on privacy settings
        user = self.request.user
        queryset = queryset.filter(Q(privacy=1) | Q(author=user))
        return queryset
    
    def get_serializer_class(self):
        if self.action in ['list', 'list_pending']:
            return PostListSerializer
        elif self.action == 'retrieve':
            return PostDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PostCreateSerializer
        return PostSerializer

    @action(detail=False, methods=['get'], url_path='pending')
    def list_pending(self, request):
        """List pending posts in groups where the user is an admin"""
        from .models import SocialGroupMember
        
        user = request.user
        # Find groups where user is admin (role=1)
        admin_groups = SocialGroupMember.objects.filter(user=user, role=1).values_list('social_group_id', flat=True)
        
        pending_posts = Post.objects.filter(
            social_group__in=admin_groups,
            status=6 # Pending
        ).order_by('-created_at')
        
        page = self.paginate_queryset(pending_posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(pending_posts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_content_counts(self, request):
        """Get counts of user's posts in a group by status"""
        social_group_id = request.query_params.get('social_group')
        if not social_group_id:
            return Response({'error': 'social_group is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        
        counts = Post.objects.filter(
            social_group_id=social_group_id,
            author=user
        ).values('status').annotate(count=Count('id'))
        
        result = {item['status']: item['count'] for item in counts}
        return Response(result)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        post = self.get_object()
        if not post.social_group:
             return Response({'error': 'Post not in a group'}, status=400)
             
        from .models import SocialGroupMember
        is_admin = SocialGroupMember.objects.filter(
            social_group=post.social_group, 
            user=request.user, 
            role=1
        ).exists()
        
        if not is_admin:
            return Response({'error': 'Permission denied'}, status=403)
            
        post.status = 3 # Published
        post.save(update_fields=['status'])
        return Response({'status': 'approved'})

    @action(detail=True, methods=['post'])
    def deny(self, request, pk=None):
        post = self.get_object()
        if not post.social_group:
             return Response({'error': 'Post not in a group'}, status=400)
             
        from .models import SocialGroupMember
        is_admin = SocialGroupMember.objects.filter(
            social_group=post.social_group, 
            user=request.user, 
            role=1
        ).exists()
        
        if not is_admin:
            return Response({'error': 'Permission denied'}, status=403)
            
        post.status = 7 # Denied
        post.save(update_fields=['status'])
        return Response({'status': 'denied'})
    
    def perform_create(self, serializer):
        """Set the author to the current user and handle file attachments"""
        from .models import PostAttachment
        
        post = serializer.save(author=self.request.user)
        
        # Handle multiple file uploads
        files = self.request.FILES.getlist('attachments')
        for index, file in enumerate(files):
            file_type = self.get_file_type(file.content_type)
            PostAttachment.objects.create(
                post=post,
                file=file,
                file_type=file_type,
                file_name=file.name,
                file_size=file.size,
                order=index
            )
        
        return post

    def perform_update(self, serializer):
        """Handle file attachments during update"""
        from .models import PostAttachment
        
        # If post status is Denied (7), reset to Pending (6) on update
        if serializer.instance.status == 7:
            post = serializer.save(status=6)
        else:
            post = serializer.save()
        
        # Handle deletions
        if hasattr(self.request.data, 'getlist'):
            attachments_to_delete = self.request.data.getlist('attachments_to_delete')
        else:
            attachments_to_delete = self.request.data.get('attachments_to_delete')
            if not isinstance(attachments_to_delete, list) and attachments_to_delete:
                attachments_to_delete = [attachments_to_delete]
            elif not attachments_to_delete:
                attachments_to_delete = []
        if attachments_to_delete:
            PostAttachment.objects.filter(id__in=attachments_to_delete, post=post).delete()
        
        # Handle multiple file uploads (add new files)
        files = self.request.FILES.getlist('attachments')
        if files:
            # Get current attachment count to determine order
            current_count = post.attachments.count()
            
            for index, file in enumerate(files):
                file_type = self.get_file_type(file.content_type)
                PostAttachment.objects.create(
                    post=post,
                    file=file,
                    file_type=file_type,
                    file_name=file.name,
                    file_size=file.size,
                    order=current_count + index + 1
                )
    
    def get_file_type(self, content_type):
        """Determine file type based on content type"""
        if content_type.startswith('image/'):
            return 'image'
        elif content_type.startswith('video/'):
            return 'video'
        elif content_type == 'application/pdf':
            return 'pdf'
        else:
            return 'document'
    
    @action(detail=True, methods=['post'])
    def toggle_pin(self, request, pk=None):
        """Toggle pin status of a post"""
        post = self.get_object()
        post.is_pinned = not post.is_pinned
        post.save()
        
        serializer = PostDetailSerializer(post, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def interact(self, request, pk=None):
        """Add or update interaction on a post"""
        post = self.get_object()
        user = request.user
        interaction_type = request.data.get('interaction_type')
        
        if not interaction_type:
            return Response({'detail': 'Interaction type is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Use update_or_create since PostInteraction uses hard delete (no soft-delete issues)
        interaction, created = PostInteraction.objects.update_or_create(
            post=post,
            user=user,
            defaults={'interaction_type': interaction_type}
        )
        
        # Update interactions count
        post.interactions_count = post.interactions.count()
        post.save()
        
        serializer = PostInteractionListSerializer(interaction, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def remove_interaction(self, request, pk=None):
        """Remove interaction from a post"""
        post = self.get_object()
        user = request.user
        
        try:
            interaction = PostInteraction.objects.get(post=post, user=user)
            interaction.delete()
            
            # Update interactions count
            post.interactions_count = post.interactions.count()
            post.save()
            
            return Response({'detail': 'Interaction removed.'}, status=status.HTTP_200_OK)
        except PostInteraction.DoesNotExist:
            return Response({'detail': 'No interaction found.'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def interactions(self, request, pk=None):
        """Get all interactions on a post with pagination"""
        from rest_framework.pagination import PageNumberPagination
        
        post = self.get_object()
        interactions = post.interactions.all()
        
        # Filter by interaction_type if provided
        interaction_type = request.query_params.get('interaction_type')
        if interaction_type:
            interactions = interactions.filter(interaction_type=interaction_type)
        
        # Apply pagination
        paginator = PageNumberPagination()
        paginator.page_size = 20  # Default page size
        paginator.page_size_query_param = 'page_size'  # Allow client to control page size
        paginator.max_page_size = 100  # Maximum allowed page size
        page = paginator.paginate_queryset(interactions, request)
        
        if page is not None:
            serializer = PostInteractionListSerializer(page, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)
        
        # Fallback if pagination fails
        serializer = PostInteractionListSerializer(interactions, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def vote(self, request, pk=None):
        """Vote on a poll"""
        post = self.get_object()
        user = request.user
        poll_option_id = request.data.get('poll_option_id')
        
        if post.post_type != 2:
            return Response({'status': 'Failed to vote','detail': 'This post is not a poll.'}, status=status.HTTP_400_BAD_REQUEST)

        if not poll_option_id:
            return Response({'status': 'Failed to vote','detail': 'Poll option ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            poll_option = PollOption.objects.get(id=poll_option_id, post=post)
        except PollOption.DoesNotExist:
            return Response({'status': 'Failed to vote','detail': 'Poll option not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Check if poll is still active
        now = timezone.now()
        if post.end_poll and now > post.end_poll:
            return Response({'status': 'Failed to vote','detail': 'This poll has ended.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if post.start_poll and now < post.start_poll:
            return Response({'status': 'Failed to vote','detail': 'This poll has not started yet.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user already voted
        existing_vote = PollVote.objects.filter(poll_option__post=post, user=user).first()
        
        if existing_vote:
            # Update vote
            old_option = existing_vote.poll_option
            existing_vote.poll_option = poll_option
            existing_vote.save()
            
            # Update vote counts
            old_option.votes_count = old_option.poll_votes.count()
            old_option.save()
            poll_option.votes_count = poll_option.poll_votes.count()
            poll_option.save()
            
            serializer = PollVoteListSerializer(existing_vote, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # Create new vote
            vote = PollVote.objects.create(
                poll_option=poll_option,
                user=user
            )
            
            # Update vote count
            poll_option.votes_count = poll_option.poll_votes.count()
            poll_option.save()
            
            serializer = PollVoteListSerializer(vote, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def remove_vote(self, request, pk=None):
        """Remove vote from a poll"""
        post = self.get_object()
        user = request.user
        
        try:
            vote = PollVote.objects.get(poll_option__post=post, user=user)
            poll_option = vote.poll_option
            vote.delete()
            
            # Update vote count
            poll_option.votes_count = poll_option.poll_votes.count()
            poll_option.save()
            
            return Response({'detail': 'Vote removed.'}, status=status.HTTP_200_OK)
        except PollVote.DoesNotExist:
            return Response({'detail': 'No vote found.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        post = self.get_object()
        comments = post.comments.all().order_by('created_at')
        serializer = PostCommentSerializer(data=comments, many=True, context={'request': request})
        serializer.is_valid()
        return Response(serializer.data, status=status.HTTP_200_OK)


    @action(detail=True, methods=['get'])
    def voters(self, request, pk=None):
        """Get all poll options with their voters for a poll post"""
        post = self.get_object()
        
        if post.post_type != 2:
            return Response({'detail': 'This post is not a poll.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get all poll options for this post with their votes
        poll_options = post.poll_options.all()
        serializer = PollOptionDetailSerializer(poll_options, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class PostCommentViewSet(viewsets.ModelViewSet):
  queryset = PostComment.objects.all()
  serializer_class = PostCommentSerializer
  ordering_fields = ['id']
  permission_classes = [IsAuthenticated]
  ordering = ('-id',)

  def get_serializer_class(self):
    if self.action == 'list':
      return PostCommentSerializer
    return PostCommentCreateSerializer
  
  def create(self, request, *args, **kwargs):
      # Use create serializer for validation/creation
      serializer = self.get_serializer(data=request.data)
      serializer.is_valid(raise_exception=True)
      instance = serializer.save()
      
      # Use full serializer for response to include nested data
      response_serializer = PostCommentSerializer(instance, context={'request': request})
      headers = self.get_success_headers(response_serializer.data)
      return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

  @action(detail=True, methods=['post'])
  def interact(self, request, pk=None):
      comment = self.get_object()
      user = request.user

      if comment.likes.filter(id=user.id).exists():
          # If the user already liked the comment, remove the like
          comment.likes.remove(user)
          return Response({'status': 'Like removed', 'like_count': comment.like_count()}, status=status.HTTP_200_OK)
      else:
          # Otherwise, add the like
          comment.likes.add(user)
          return Response({'status': 'Like added', 'like_count': comment.like_count()}, status=status.HTTP_200_OK)

class PostInteractionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PostInteraction.objects.all()
    serializer_class = PostInteractionSerializer
    permission_classes = [IsAuthenticated]
    ordering_fields = ['id', 'created_at']
    ordering = ('-id',)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PostInteractionListSerializer
        return PostInteractionSerializer


class PollVoteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PollVote.objects.all()
    serializer_class = PollVoteSerializer
    permission_classes = [IsAuthenticated]
    ordering_fields = ['id', 'created_at']
    ordering = ('-id',)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PollVoteListSerializer
        return PollVoteSerializer


class UserSocialProfileFilter(FilterSet):
    search = django_filters.CharFilter(method='elastic_search')
    not_in_group = django_filters.NumberFilter(method='not_in_group_filter')
    
    class Meta:
        model = UserSocialProfile
        fields = ['user']
    
    def elastic_search(self, queryset, name, value):
        if not value:
            return queryset
        fields = ['user__username__icontains', 'user__first_name__icontains', 'user__last_name__icontains', 'user__email__icontains']
        _q = Q()
        for field in fields:
            _q = _q | Q(**{field: value})
        return queryset.filter(_q)

    def not_in_group_filter(self, queryset, name, value):
        """Filter out users who are already in the specified group"""
        if not value:
            return queryset
        
        # Get all user IDs that are already in the group
        users_in_group = SocialGroupMember.objects.filter(social_group=value).values_list('user_id', flat=True)
        
        # Return only users who are NOT in the group
        return queryset.exclude(user_id__in=users_in_group)

class UserSocialProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for user social profiles"""
    queryset = UserSocialProfile.objects.all()
    serializer_class = UserSocialProfileSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = UserSocialProfileFilter
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    
    def get_queryset(self):
        """Filter profiles based on user permissions"""
        return UserSocialProfile.objects.select_related('user').all()
    
    def retrieve(self, request, *args, **kwargs):
        """Get user profile by user ID"""
        user_id = kwargs.get('pk')
        try:
            profile = UserSocialProfile.objects.get(user_id=user_id)
        except UserSocialProfile.DoesNotExist:
            # Auto-create profile if doesn't exist
            from django.contrib.auth.models import User
            user = User.objects.get(id=user_id)
            profile = UserSocialProfile.objects.create(user=user)
        
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """Update user profile - only allow users to update their own profile"""
        user_id = kwargs.get('pk')
        if request.user.id != int(user_id):
            return Response(
                {'error': 'You can only update your own profile'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            profile = UserSocialProfile.objects.get(user_id=user_id)
        except UserSocialProfile.DoesNotExist:
            profile = UserSocialProfile.objects.create(user=request.user)
        
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        """Get user's posts with privacy filtering"""
        user_id = pk
        requesting_user = request.user
        
        # Check if users are friends
        are_friends = Friendship.objects.filter(
            Q(from_user_id=requesting_user.id, to_user_id=user_id, status=2) |
            Q(from_user_id=user_id, to_user_id=requesting_user.id, status=2)
        ).exists()
        
        # Filter posts based on privacy
        posts = Post.objects.filter(author_id=user_id)
        
        if requesting_user.id != int(user_id):
            # Not viewing own profile
            if are_friends:
                # Show public and friends-only posts
                posts = posts.filter(privacy__in=[1, 2])
            else:
                # Show only public posts
                posts = posts.filter(privacy=1)
        
        posts = posts.order_by('-created_at')
        serializer = PostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)
