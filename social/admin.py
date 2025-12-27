from django.contrib import admin
from .models import SocialGroup, SocialGroupMember, Post, PollOption, PostInteraction, PollVote


@admin.register(SocialGroup)
class SocialGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_public', 'created_at', 'updated_at']
    list_filter = ['is_public', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['-created_at']


@admin.register(SocialGroupMember)
class SocialGroupMemberAdmin(admin.ModelAdmin):
    list_display = ['id', 'social_group', 'user', 'role', 'status', 'created_at']
    list_filter = ['role', 'status', 'created_at']
    search_fields = ['social_group__name', 'user__username']
    ordering = ['-created_at']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author', 'social_group', 'post_type', 'is_pinned', 'interactions_count', 'comments_count', 'created_at']
    list_filter = ['post_type', 'is_pinned', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    ordering = ['-created_at']


@admin.register(PollOption)
class PollOptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'post', 'option', 'votes_count']
    search_fields = ['option', 'post__title']
    ordering = ['post', 'id']


@admin.register(PostInteraction)
class PostInteractionAdmin(admin.ModelAdmin):
    list_display = ['id', 'post', 'user', 'interaction_type', 'created_at']
    list_filter = ['interaction_type', 'created_at']
    search_fields = ['post__title', 'user__username']
    ordering = ['-created_at']


@admin.register(PollVote)
class PollVoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'poll_option', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['poll_option__option', 'user__username']
    ordering = ['-created_at']
