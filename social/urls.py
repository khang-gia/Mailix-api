from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SocialGroupViewSet,
    SocialGroupMemberViewSet,
    PostViewSet,
    PostInteractionViewSet,
    PollVoteViewSet,
    PostCommentViewSet
)

router = DefaultRouter()
router.register(r'groups', SocialGroupViewSet, basename='socialgroup')
router.register(r'members', SocialGroupMemberViewSet, basename='socialgroupmember')
router.register(r'posts', PostViewSet, basename='post')
router.register(r'interactions', PostInteractionViewSet, basename='postinteraction')
router.register(r'votes', PollVoteViewSet, basename='pollvote')
router.register(r'post_comments', PostCommentViewSet, basename='postcomment')
urlpatterns = [
    path('', include(router.urls)),
]
