from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from main.models import Reaction, Post, Comment
from auth_.models import CustomUser
from main.serializers import ReactionSerializer, ReactionFullSerializer
from main.permissions import GetPostPermission
from auth_.permissions import FriendPermission


def get_post_type(post):
    return 1 if post.__class__.__name__ == 'Post' else 2


class ReactionDetailView(APIView):
    def get(self, request, pk):
        reaction = Reaction.objects.get(id=pk)
        serializer = ReactionFullSerializer(reaction)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        if not request.user.is_authenticated:
            return Response("Authentication required.", status=status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED)
        try:
            reaction = Reaction.objects.get(id=pk)
        except:
            return Response("Reaction not found.", status=status.HTTP_404_NOT_FOUND)
        if request.user != reaction.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = ReactionSerializer(instance=reaction, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors)

    def delete(self, request, pk):
        try:
            reaction = Reaction.objects.get(id=pk)
        except:
            return Response("Reaction not found.", status=status.HTTP_404_NOT_FOUND)
        if request.user != reaction.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        reaction.delete()
        return Response(status=status.HTTP_200_OK)


class PostReactionsView(APIView):
    def get(self, request, pk):
        try:
            post = Post.objects.get(id=pk)
        except:
            return Response("Post not found.", status=status.HTTP_404_NOT_FOUND)

        if not GetPostPermission.user_obj_permission(request.user, post):
            return Response("You have no permission.", status=status.HTTP_401_UNAUTHORIZED)

        reactions = post.reactions
        serializer = ReactionFullSerializer(reactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk):
        if not request.user.is_authenticated:
            return Response("Authentication required.", status=status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED)

        serializer = ReactionFullSerializer(data=request.data)
        if serializer.is_valid():
            try:
                post = Post.objects.get(id=pk)
            except:
                return Response("Post not found.", status=status.HTTP_404_NOT_FOUND)

            if Reaction.objects.filter(user=request.user.id, post_instance=pk).exists():
                return Response("user and post must be unique together",
                                status=status.HTTP_400_BAD_REQUEST)

            if not GetPostPermission.user_obj_permission(request.user, post):
                return Response("You have no permission.", status=status.HTTP_401_UNAUTHORIZED)

            serializer.save(user=self.request.user, post=post)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CommentReactionsView(APIView):
    def get(self, request, pk):
        try:
            comment = Comment.objects.get(id=pk)
        except:
            return Response("Comment not found.", status=status.HTTP_404_NOT_FOUND)

        if not GetPostPermission.user_obj_permission(request.user, comment.post):
            return Response("You have no permission.", status=status.HTTP_401_UNAUTHORIZED)

        reactions = comment.reactions
        serializer = ReactionFullSerializer(reactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk):
        if not request.user.is_authenticated:
            return Response("Authentication required.", status=status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED)

        serializer = ReactionFullSerializer(data=request.data)
        if serializer.is_valid():
            try:
                comment = Comment.objects.get(id=pk)
            except:
                return Response("Comment not found.", status=status.HTTP_404_NOT_FOUND)

            if Reaction.objects.filter(user_id=request.user.id, comment_instance=pk).exists():
                return Response("user and comment must be unique together",
                                status=status.HTTP_400_BAD_REQUEST)

            if not GetPostPermission.user_obj_permission(request.user, comment.post):
                return Response("You have no permission.", status=status.HTTP_401_UNAUTHORIZED)

            serializer.save(user=self.request.user, post=comment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserReactionsView(APIView):
    def get(self, request, pk):
        try:
            user = CustomUser.objects.get(id=pk)
        except:
            return Response("Post not found.", status=status.HTTP_404_NOT_FOUND)

        if not FriendPermission.user_obj_permission(request.user, user):
            return Response("You have no permission.", status=status.HTTP_401_UNAUTHORIZED)

        reactions = user.reactions
        serializer = ReactionFullSerializer(reactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
