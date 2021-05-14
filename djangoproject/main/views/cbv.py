from rest_framework.views import APIView
from django.http import JsonResponse, HttpResponse
from rest_framework.response import Response
from rest_framework import status
from main.serializers import PostSerializer, CommentSerializer
from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework import generics
from main.models import Group, Post, Comment


class GroupPostView(APIView):
    def get(self, request, pk):
        posts = Post.objects.filter(group_id=pk)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=self.request.user, group_id=pk)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class post_comments(APIView):
    def get(self, request, pk):
        try:
            post = Post.objects.get(id=pk)
        except Post.DoesNotExist as e:
            return Response(status=status.HTTP_404_NOT_FOUND)
        comments = post.comments.filter(directed_to__isnull=True)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=self.request.user, post_id=pk)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class comment_detail(APIView):
    def exist(self, pk1, pk2):
        try:
            post = Post.objects.get(id=pk1)
        except Post.DoesNotExist as e:
            return False
        try:
            comment = Comment.objects.get(id=pk2)
        except Comment.DoesNotExist as e:
            return False
        return True

    def get(self, request, pk, pk2):
        if self.exist(pk, pk2) == False:
            return Response(status=status.HTTP_404_NOT_FOUND)
        comment = Comment.objects.get(id=pk2)
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk, pk2):
        if self.exist(pk, pk2) == False:
            return Response(status=status.HTTP_404_NOT_FOUND)
        comment = Comment.objects.get(id=pk2)
        if request.user != comment.created_by:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        comment.delete()
        return Response(status=status.HTTP_200_OK)

    def put(self, request, pk, pk2):
        if self.exist(pk, pk2) == False:
            return Response(status=status.HTTP_404_NOT_FOUND)
        comment = Comment.objects.get(id=pk2)
        if request.user != comment.created_by:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = CommentSerializer(instance=comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors)
