from main.views.viewsets import GroupViewSet, PostViewSet, CommentViewSet,\
    FriendRequestViewSet, GroupJoinRequestViewSet, GroupInviteViewSet, NotificationViewSet
from main.views.cbv import ReactionDetailView, PostReactionsView, CommentReactionsView, UserReactionsView
from rest_framework import routers
from django.urls import path

router = routers.SimpleRouter()
router.register('groups', GroupViewSet, basename='groups')
router.register('posts', PostViewSet, basename='posts')
router.register('comments', CommentViewSet, basename='comments')
router.register('friend_requests', FriendRequestViewSet, basename='friend_requests')
router.register('group_join_requests', GroupJoinRequestViewSet, basename='group_join_requests')
router.register('group_invites', GroupInviteViewSet, basename='group_invites')
router.register('notifications', NotificationViewSet, basename='notifications')

urlpatterns = [
    path('reactions/<int:pk>/', ReactionDetailView.as_view()),
    path('posts/<int:pk>/reactions/', PostReactionsView.as_view()),
    path('comments/<int:pk>/reactions/', CommentReactionsView.as_view()),
    path('users/<int:pk>/reactions/', UserReactionsView.as_view())
]
urlpatterns += router.urls
