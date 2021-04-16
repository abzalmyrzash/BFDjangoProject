from rest_framework.views import APIView

from api.models import  Group,Comment,Post, CustomUser
from api.serializers import UserSerializer,  GroupSerializer,CommentSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from rest_framework import filters

from django_filters.rest_framework import DjangoFilterBackend




class Groups(generics.ListCreateAPIView):
    def get_queryset(self):
        return Group.objects.all()

    def get_serializer_class(self):
        return GroupSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    filter_backends = (DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter)

    search_fields = ('name', )


class GroupDetail(generics.RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        print(self.request)
        return Group.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    serializer_class = GroupSerializer


class SubscribedGroups(generics.ListAPIView):
    def get_queryset(self):
        return Group.objects.filter(subscribers__id=self.request.user.id)

    def get_serializer_class(self):
        return GroupSerializer


class CreatedGroups(generics.ListAPIView):
    def get_queryset(self):
        return Group.objects.filter(created_by_id=self.request.user.id)

    def get_serializer_class(self):
        return GroupSerializer


class UserDetail(generics.RetrieveAPIView):
    def get_queryset(self):
        return CustomUser.objects.all()

    def get_serializer_class(self):
        return UserSerializer
