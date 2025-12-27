from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import FilterSet
import django_filters
from django.db.models import Q, F
from django.utils import timezone

from .models import SocialGroup, SocialGroupMember, Post, PollOption, PostInteraction, PollVote, PostComment
from .serializers import (
    SocialGroupSerializer, SocialGroupListSerializer, SocialGroupDetailSerializer,
    SocialGroupMemberSerializer, SocialGroupMemberListSerializer,
    PostSerializer, PostListSerializer, PostDetailSerializer, PostCreateSerializer,
    PollOptionSerializer, PollOptionDetailSerializer,
    PostInteractionSerializer, PostInteractionListSerializer,
    PollVoteSerializer, PollVoteListSerializer, PostCommentSerializer,  PostCommentCreateSerializer
)


class SocialGroupFilter(FilterSet):
    search = django_filters.CharFilter(method='elastic_search')
    
    class Meta:
        model = SocialGroup
        fields = ['name', 'is_public']
    
    def elastic_search(self, queryset, name, value):
        if not value:
            return queryset
        fields = ['name__icontains', 'description__icontains']
        _q = Q()
        for field in fields:
            _q = _q | Q(**{field: value})
        return queryset.filter(_q)


class SocialGroupViewSet(viewsets.ModelViewSet):
    queryset = SocialGroup.objects.all()
    serializer_class = SocialGroupSerializer
    filterset_class = SocialGroupFilter
    permission_classes = [IsAuthenticated]
    ordering_fields = ['id', 'created_at']
    ordering = ('-id',)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SocialGroupListSerializer
        elif self.action == 'retrieve':
            return SocialGroupDetailSerializer
        return SocialGroupSerializer
    
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
    
    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        """Get all posts in a social group"""
        group = self.get_object()
        posts = group.posts.all().order_by('-is_pinned', '-created_at')
        serializer = PostListSerializer(posts, many=True, context={'request': request})
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
    
    class Meta:
        model = Post
        fields = ['social_group', 'author', 'post_type', 'is_pinned', 'status']
    
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
        if self.action == 'list':
            return PostListSerializer
        elif self.action == 'retrieve':
            return PostDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PostCreateSerializer
        return PostSerializer
    
    def perform_create(self, serializer):
        """Set the author to the current user"""
        serializer.save(author=self.request.user)
    
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
        """Get all interactions on a post"""
        post = self.get_object()
        interactions = post.interactions.all()
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
    
    @action(detail=True, methods=['delete'])
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
