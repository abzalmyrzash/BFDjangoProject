from main.views.viewsets import GroupViewSet, PostViewSet, CommentViewSet,\
    FriendRequestViewSet, GroupJoinRequestViewSet, GroupInviteViewSet
from rest_framework import routers

router = routers.SimpleRouter()
router.register('groups', GroupViewSet, basename='groups')
router.register('posts', PostViewSet, basename='posts')
router.register('comments', CommentViewSet, basename='comments')
router.register('friend_requests', FriendRequestViewSet, basename='friend_requests')
router.register('group_join_requests', GroupJoinRequestViewSet, basename='group_join_requests')
router.register('group_invites', GroupInviteViewSet, basename='group_invites')

urlpatterns = []
urlpatterns += router.urls
