from django.shortcuts import render

from rest_framework import generics, mixins, viewsets
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
        elif self.action in ['update', 'partial update']:
            return UserUpdateSerializer
        else:
            return UserFullSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create']:
            permission_classes = (AllowAny,)
        else:
            permission_classes = (IsExactUserPermission,)

        return [permission() for permission in permission_classes]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


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
