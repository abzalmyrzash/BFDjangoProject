from django.shortcuts import render
import logging
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from main.models import Group, Post, Comment, Reaction, FriendRequest, GroupJoinRequest, GroupInvite
from main.serializers import GroupSerializer, PostSerializer, CommentSerializer, ReactionSerializer,\
    FriendRequestSerializer, GroupJoinRequestSerializer, GroupInviteSerializer,\
    GroupFullSerializer, PostFullSerializer, PostWithoutContentSerializer, \
    CommentFullSerializer, ReactionFullSerializer
from auth_.serializers import UserSerializer
from auth_.models import CustomUser
from rest_framework.permissions import IsAuthenticated, AllowAny
from main.permissions import GroupMemberPermission, GroupAdminPermission, GroupOwnerPermission,\
    PostCreatorPermission, GetPostPermission

logger = logging.getLogger(__name__)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()

    def get_permissions(self):
        """
        - Anyone can retrieve general group information
        - Only authenticated users can create groups
        - Only group owners can add/drop admins, transfer ownership, and delete their group
        - Only group admins can update basic group info (name, description) and kick members
        - Only group members can leave the group
        """
        print(self.action)
        if self.action in ['list', 'retrieve']:
            permission_classes = (AllowAny,)
        elif self.action in ['create']:
            permission_classes = (IsAuthenticated,)
        elif self.action in ['add_drop_admin', 'change_owner', 'destroy']:
            permission_classes = (GroupOwnerPermission,)
        elif self.action in ['kick_member', 'update', 'partial_update']:
            permission_classes = (GroupAdminPermission,)
        elif self.action in ['leave']:
            permission_classes = (GroupMemberPermission,)
        else:
            permission_classes = (AllowAny,)

        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'list':
            return GroupSerializer
        else:
            return GroupFullSerializer

    def perform_create(self, serializer):
        owner = self.request.user
        group = serializer.save(created_by_username=owner.username, owner=owner)
        group.admins.add(owner)
        group.members.add(owner)

        logger.info(f'Group created: {serializer.instance}')

    def perform_update(self, serializer):
        serializer.save()
        logger.info(f'Group updated: {serializer.instance}')

    def perform_destroy(self, instance):
        instance.delete()
        logger.warning(f'Group deleted: {instance}')

    @action(methods=['POST', 'DELETE'], detail=True, url_path='add_drop_admin', url_name='add_drop_admin')
    def add_drop_admin(self, request, pk=None):
        group = self.get_object()
        user_id = int(request.data['user_id'])

        is_member = group.has_member(user_id)
        if not is_member:
            return Response('User is not a group member.', status=status.HTTP_400_BAD_REQUEST)

        is_admin = group.has_admin(user_id)
        user = CustomUser.objects.get(id=user_id)

        if request.method == 'POST':
            if is_admin:
                return Response('User is already a group admin.', status=status.HTTP_400_BAD_REQUEST)
            group.admins.add(user)
            group.save()
            logger.info(f'admin {user_id} added')
            return Response(f'admin {user_id} added.', status=status.HTTP_200_OK)
        elif request.method == 'DELETE':
            if not is_admin:
                return Response('User is not a group admin.', status=status.HTTP_400_BAD_REQUEST)
            if group.owner.id == user_id:
                return Response('Owner cannot be removed from admins.', status=status.HTTP_400_BAD_REQUEST)
            group.admins.remove(user)
            group.save()
            logger.info(f'admin {user_id} removed')
            return Response(f'admin {user_id} removed', status=status.HTTP_200_OK)

    @action(methods=['PATCH'], detail=True, url_path='change_owner', url_name='change_owner')
    def change_owner(self, request, pk=None):
        group = self.get_object()
        user_id = int(request.data['user_id'])

        if request.user.id == user_id:
            return Response('Why are you trying to transfer ownership to yourself when you are already the owner?',
                            status=status.HTTP_400_BAD_REQUEST)

        if not group.has_member(user_id):
            return Response('User is not a group member.', status=status.HTTP_400_BAD_REQUEST)
        user = CustomUser.objects.get(id=user_id)
        group.owner = user
        group.admins.add(user)
        group.save()
        logger.info(f"Owner changed to {user} in group {group}")
        return Response(f"Owner changed to {user} in group {group}", status=status.HTTP_200_OK)

    @action(methods=['DELETE'], detail=True, url_path='kick_member', url_name='kick_member')
    def kick_member(self, request, pk=None):
        group = self.get_object()
        user_id = int(request.data['user_id'])

        if request.user.id == user_id:
            return Response(f"Kicking yourself is not the way to leave!", status=status.HTTP_400_BAD_REQUEST)

        if not group.has_member(user_id):
            return Response(f"User is not a group member.", status=status.HTTP_400_BAD_REQUEST)

        if group.owner.id == user_id:
            return Response(f"The owner cannot be kicked.", status=status.HTTP_400_BAD_REQUEST)

        if group.has_admin(user_id) and group.owner.id != request.user.id:
            return Response(f"Only the owner can kick admins.", status=status.HTTP_401_UNAUTHORIZED)

        user = CustomUser.objects.get(id=user_id)
        group.admins.remove(user)
        group.members.remove(user)
        return Response(f"Member {user} was kicked successfully.", status=status.HTTP_200_OK)

    @action(methods=['DELETE'], detail=True, url_path='leave', url_name='leave')
    def leave(self, request, pk=None):
        group = self.get_object()
        group.members.remove(request.user)
        group.admins.remove(request.user)
        if group.owner and group.owner.id == request.user.id:
            group.owner = None

        group.save()
        logger.info(f"User {request.user} left group {group}")
        return Response(f"User {request.user} left group {group}", status=status.HTTP_200_OK)



class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return PostWithoutContentSerializer
        else:
            return PostFullSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = (PostCreatorPermission,)
        elif self.action in ['create']:
            permission_classes = (IsAuthenticated,)
        elif self.action in ['retrieve']:
            permission_classes = (GetPostPermission,)
        # elif self.action in ['get_by_creator']:
        #     permission_classes = (FriendPermission,)
        # elif self.action in ['get_by_group']:
        #     permission_classes = (GroupMemberPermission,)
        else:
            permission_classes = (AllowAny,)

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        created_by = self.request.user
        try:
            is_private = serializer.validated_data.pop('is_private')
        except KeyError:
            is_private = False

        group_id = serializer.validated_data.pop('group_id')

        post = serializer.save(created_by=created_by, is_private=is_private)
        post.group = Group.objects.get(id=group_id)
        post.save()
        logger.info(f'Post created: {serializer.instance}')

    def perform_update(self, serializer):
        serializer.save()
        logger.info(f'Post updated: {serializer.instance}')

    def perform_destroy(self, instance):
        instance.delete()
        logger.warning(f'Post deleted: {instance}')

    @action(methods=['GET'], detail=True, url_path='get_by_creator', url_name='get_by_creator')
    def get_by_creator(self, request, pk):
        queryset = Post.objects.get_by_creator(creator=pk)
        serializer = PostWithoutContentSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['GET'], detail=True, url_path='get_by_group', url_name='get_by_group')
    def get_by_group(self, request, pk):
        queryset = Post.objects.get_by_group(group=pk)
        serializer = PostWithoutContentSerializer(queryset, many=True)
        return Response(serializer.data)



class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return CommentSerializer
        else:
            return CommentFullSerializer

    def perform_create(self, serializer):
        serializer.save()
        logger.info(f'Comment created: {serializer.instance}')

    def perform_update(self, serializer):
        serializer.save()
        logger.info(f'Comment updated: {serializer.instance}')

    def perform_destroy(self, instance):
        instance.delete()
        logger.warning(f'Comment deleted: {instance}')



class ReactionViewSet(viewsets.ModelViewSet):
    queryset = Reaction.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return ReactionSerializer
        else:
            return ReactionFullSerializer

    def perform_create(self, serializer):
        serializer.save()
        logger.info(f'Reaction created: {serializer.instance}')

    def perform_update(self, serializer):
        serializer.save()
        logger.info(f'Reaction updated: {serializer.instance}')

    def perform_destroy(self, instance):
        instance.delete()
        logger.warning(f'Reaction deleted: {instance}')



class FriendRequestViewSet(viewsets.ModelViewSet):
    queryset = FriendRequest.objects.all()

    def get_serializer_class(self):
        return FriendRequestSerializer

    def perform_create(self, serializer):
        serializer.save()
        logger.info(f'Friend request created: {serializer.instance}')

    def perform_update(self, serializer):
        serializer.save()
        logger.info(f'friend request updated: {serializer.instance}')

    def perform_destroy(self, instance):
        instance.delete()
        logger.warning(f'Group deleted: {instance}')



class GroupJoinRequestViewSet(viewsets.ModelViewSet):
    queryset = GroupJoinRequest.objects.all()

    def get_serializer_class(self):
        return GroupJoinRequestSerializer

    def perform_create(self, serializer):
        serializer.save()
        logger.info(f'Group join request created: {serializer.instance}')

    def perform_update(self, serializer):
        serializer.save()
        logger.info(f'Group join request updated: {serializer.instance}')

    def perform_destroy(self, instance):
        instance.delete()
        logger.warning(f'Group join request deleted: {instance}')



class GroupInviteViewSet(viewsets.ModelViewSet):
    queryset = GroupInvite.objects.all()

    def get_serializer_class(self):
        return GroupInviteSerializer

    def perform_create(self, serializer):
        serializer.save()
        logger.info(f'Group invite created: {serializer.instance}')

    def perform_update(self, serializer):
        serializer.save()
        logger.info(f'Group invite updated: {serializer.instance}')

    def perform_destroy(self, instance):
        instance.delete()
        logger.warning(f'Group invite deleted: {instance}')
