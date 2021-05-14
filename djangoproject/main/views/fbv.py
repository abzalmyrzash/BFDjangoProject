
from django.http import JsonResponse,HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from main.serializers import PostSerializer, CommentSerializer
from main.models import Group,Post, Comment, CustomUser


@api_view(['GET','DELETE','PUT'])
def post_detail(request,pk2):
    try:
        post=Post.objects.get(id=pk2)
    except Post.DoesNotExist as e:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializer=PostSerializer(post)
        return Response(serializer.data)

    if request.user!=post.created_by:
        return Response('not correct user')

    if request.method == 'DELETE':
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    if request.method == 'PUT':

        serializer=PostSerializer(instance=post,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def comment_replies(request, pk1, pk2):
    try:
        comment = Comment.objects.get(id=pk2)
    except Comment.DoesNotExist as e:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        replies = comment.replies
        serializer = CommentSerializer(replies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    if request.method == 'POST':
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user, directed_to_id=pk2, post_id=pk1)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
def post_like(request, pk):
    try:
        post = Post.objects.get(id=pk)
    except Comment.DoesNotExist as e:
        return Response(status=status.HTTP_404_NOT_FOUND)

    liked = False
    if post.likes.filter(pk=request.user.id).exists():
        liked = True

    if request.method == 'GET':
        return Response({"liked": liked, "like_count": post.likes.all().count()}, status=status.HTTP_200_OK)

    if request.method == 'POST':
        if liked:
            post.likes.remove(request.user)
            post.created_by.reputation -= 1
            liked = False
        else:
            post.likes.add(request.user)
            post.created_by.reputation += 1
            liked = True

        post.save()
        post.created_by.save()
        return Response({"liked": liked, "like_count": post.likes.all().count()}, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
def comment_like(request, post_pk, pk):
    try:
        post = Post.objects.get(id=post_pk)
    except Post.DoesNotExist as e:
        return Response(status=status.HTTP_404_NOT_FOUND)

    try:
        comment = Comment.objects.get(id=pk)
    except Comment.DoesNotExist as e:
        return Response(status=status.HTTP_404_NOT_FOUND)

    liked = False
    if comment.likes.filter(pk=request.user.id).exists():
        liked = True

    if request.method == 'GET':
        return Response({"liked": liked, "like_count": comment.likes.all().count()}, status=status.HTTP_200_OK)

    if request.method == 'POST':
        if not liked:
            comment.likes.add(request.user)
            comment.created_by.reputation += 1
            liked = True
        else:
            comment.likes.remove(request.user)
            comment.created_by.reputation -= 1
            liked = False

        comment.save()
        comment.created_by.save()
        return Response({"liked": liked, "like_count": comment.likes.all().count()}, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
def subscribe(request, pk):
    try:
        group = Group.objects.get(id=pk)
    except Group.DoesNotExist as e:
        return Response(status=status.HTTP_404_NOT_FOUND)

    subscribed = False
    if group.subscribers.filter(pk=request.user.id).exists():
        subscribed = True

    if request.method == 'GET':
        return Response({"subscribed": subscribed, "subscriber_count": group.subscribers.all().count()},
                        status=status.HTTP_200_OK)

    if request.method == 'POST':
        if not subscribed:
            group.subscribers.add(request.user)
            subscribed = True
        else:
            group.subscribers.remove(request.user)
            subscribed = False

        group.save()
        return Response({"subscribed": subscribed, "subscriber_count": group.subscribers.all().count()}, status=status.HTTP_200_OK)