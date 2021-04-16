from api.models import CustomUser
from api.serializers import UserSerializer
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView
from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated, AllowAny


class UserList(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, )


@api_view(['POST'])
def login(request):
    serializer = AuthTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data.get('user')
    token, created = Token.objects.get_or_create(user=user)
    return Response({'token': token.key})


@api_view(['POST'])
def logout(request):
    request.auth.delete()
    return Response(status=status.HTTP_200_OK)


class CreateUserView(CreateAPIView):

    model = get_user_model()
    permission_classes = [
        permissions.AllowAny # Or anon users can't register
    ]
    serializer_class = UserSerializer


@api_view(['GET'])
def current_user(request):
    if request.method == 'GET':
        serializer = UserSerializer(request.user)
        print(request.user.id, request.user.username)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def set_password(request, pk):
    if request.method == 'POST':
        old_password = request.data['old_password']
        new_password = request.data['new_password']
        user = CustomUser.objects.get(id=pk)

        username = user.username

        serializer = AuthTokenSerializer(data={"username": username, "password": old_password})
        serializer.is_valid(raise_exception=True)

        user.set_password(new_password)
        user.save()
        return Response(status=status.HTTP_200_OK)
