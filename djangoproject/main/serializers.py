from rest_framework import serializers
from .models import Group, Post, Comment, Reaction, FriendRequest, GroupJoinRequest, GroupInvite
from auth_.serializers import UserSerializer
from utils.constants import REACTION_TYPES


class GroupSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField(read_only=True)
    # name = serializers.CharField(required=True)
    # created_by = UserSerializer(read_only=True)
    # created_at = serializers.DateTimeField(read_only=True)
    class Meta:
        model = Group
        fields = ('id', 'name', 'description', 'photo')


class GroupFullSerializer(GroupSerializer):
    owner = UserSerializer(read_only=True)
    admins = UserSerializer(many=True, read_only=True)
    members = UserSerializer(many=True, read_only=True)
    created_by_username = serializers.CharField(max_length=150, read_only=True)

    class Meta(GroupSerializer.Meta):
        fields = GroupSerializer.Meta.fields + ('created_by_username', 'created_at', 'owner', 'admins', 'members')


class PostWithoutContentSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    created_by = UserSerializer(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    group = GroupSerializer(read_only=True)
    is_private = serializers.BooleanField(read_only=True)


class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ('id', 'title', 'body', 'image')


class PostFullSerializer(PostSerializer):
    created_by = UserSerializer(read_only=True)
    group = GroupSerializer(read_only=True)
    group_id = serializers.IntegerField(write_only=True, allow_null=True)

    def validate_group_id(self, value):
        if not Group.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"Group not found.")
        user = self.context['request'].user
        if user not in Group.objects.get(id=value).members.all():
            raise serializers.ValidationError(f"You are not the group's member.")
        return value

    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + ('created_by', 'created_at', 'group', 'group_id', 'is_private')


class CommentWithoutContentSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    created_by = UserSerializer(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    post = GroupSerializer(read_only=True)
    directed_to = serializers.PrimaryKeyRelatedField(read_only=True)
    is_private = serializers.BooleanField(read_only=True)


class CommentSerializer(serializers.ModelSerializer):
    # body = serializers.CharField(max_length=1000, required=True)

    class Meta:
        model = Comment
        fields = ('id', 'body')


class CommentFullSerializer(CommentSerializer):
    created_by = UserSerializer
    post = PostWithoutContentSerializer

    class Meta(CommentSerializer.Meta):
        fields = CommentSerializer.Meta.fields + ('created_by', 'created_by', 'created_at', 'post', 'directed_to')


class ReactionSerializer(serializers.ModelSerializer):
    def validate_type(self, value):
        for reactionType in REACTION_TYPES:
            if reactionType[0] == value:
                return value
        raise serializers.ValidationError('Invalid reaction type')

    class Meta:
        model = Reaction
        fields = ('id', 'type')


class ReactionFullSerializer(ReactionSerializer):
    post = PostSerializer
    user = UserSerializer

    class Meta(ReactionSerializer.Meta):
        fields = ReactionSerializer.Meta.fields + ('user', 'post')


class AbstractRequestSerializer(serializers.ModelSerializer):
    from_user = UserSerializer

    class Meta:
        fields = ('id', 'from_user', 'sent_at', 'status', 'message')


class FriendRequestSerializer(AbstractRequestSerializer):
    to_user = UserSerializer

    class Meta(AbstractRequestSerializer.Meta):
        model = FriendRequest
        fields = AbstractRequestSerializer.Meta.fields + ('to_user',)


class GroupJoinRequestSerializer(AbstractRequestSerializer):
    to_group = GroupSerializer

    class Meta(AbstractRequestSerializer.Meta):
        model = GroupJoinRequest
        fields = AbstractRequestSerializer.Meta.fields + ('to_group',)


class GroupInviteSerializer(AbstractRequestSerializer):
    group = GroupSerializer
    to_user = UserSerializer

    class Meta(AbstractRequestSerializer.Meta):
        model = GroupInvite
        fields = AbstractRequestSerializer.Meta.fields + ('group', 'to_user')
