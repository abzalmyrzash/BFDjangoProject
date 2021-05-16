from django.shortcuts import render

from rest_framework import generics, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.decorators import api_view
from rest_framework_jwt.serializers import JSONWebTokenSerializer, VerifyJSONWebTokenSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.response import Response

from auth_.models import CustomUser, Profile
from auth_.serializers import UserSerializer, UserFullSerializer, UserUpdateSerializer, ProfileSerializer
from auth_.permissions import ProfileOwnerPermission, FriendPermission, IsExactUserPermission

import logging

logger = logging.getLogger(__name__)

# Create your views here.


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return UserSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        else:
            return UserFullSerializer

    def get_permissions(self):
        print(self.action)
        if self.action in ['list', 'retrieve', 'create']:
            permission_classes = (AllowAny,)
        else:
            permission_classes = (IsExactUserPermission,)

        return [permission() for permission in permission_classes]




class ProfileViewSet(viewsets.GenericViewSet,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin):
    queryset = Profile.objects.all()

    def get_serializer_class(self):
        return ProfileSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            permission_classes = (ProfileOwnerPermission,)
        else:
            permission_classes = (AllowAny,)

        return [permission() for permission in permission_classes]

    def perform_update(self, serializer):
        serializer.save()
        logger.info(f'Profile updated: {serializer.instance}')

    @action(methods=['GET'], detail=True, url_path='get_by_user', url_name='get_by_user')
    def get_by_user(self, request, pk):
        pk = int(pk)
        if not CustomUser.objects.filter(id=pk).exists():
            return Response("User not found.", status=status.HTTP_404_NOT_FOUND)
        profile = Profile.objects.get(user_id=pk)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)


@api_view(['POST'])
def change_password(request, pk):
    if request.method == 'POST':
        old_password = request.data['old_password']
        new_password = request.data['new_password']
        user = CustomUser.objects.get(id=pk)

        username = user.username

        serializer = JSONWebTokenSerializer(data={"username": username, "password": old_password})
        serializer.is_valid(raise_exception=True)

        user.set_password(new_password)
        user.save()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
def current_user(request):
    if request.method == 'GET':
        serializer = UserSerializer(request.user)
        print(request.user.id, request.user.username)
        return Response(serializer.data, status=status.HTTP_200_OK)
