from rest_framework import serializers
from .models import Group, Post, Comment


class GroupSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField(read_only=True)
    # name = serializers.CharField(required=True)
    # created_by = UserSerializer(read_only=True)
    # created_at = serializers.DateTimeField(read_only=True)
    class Meta:
        model = Group
        fields = ('id', 'name', 'created_by', 'created_at')


class PostSerializer(serializers.ModelSerializer):
    # title = serializers.CharField(required=True)
    # group = GroupSerializer()

    class Meta:
        model = Post
        fields = ('id', 'title', 'body', 'created_by', 'created_at', 'group')


class CommentSerializer(serializers.ModelSerializer):
    # body = serializers.CharField(max_length=1000, required=True)

    class Meta:
        model = Comment
        fields = ('id', 'body', 'created_by', 'created_at', 'post', 'directed_to')