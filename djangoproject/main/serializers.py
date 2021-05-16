from rest_framework import serializers
from .models import Group, Post, Comment, Reaction, FriendRequest, GroupJoinRequest, GroupInvite, Notification
from auth_.serializers import UserSerializer
from utils.constants import REACTION_TYPES
from main.permissions import GetPostPermission


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
        fields = ('id', 'title', 'body', 'image', 'is_private')


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
        fields = PostSerializer.Meta.fields + ('created_by', 'created_at', 'group', 'group_id')


class CommentWithoutContentSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    created_by = UserSerializer(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    post = PostWithoutContentSerializer(read_only=True)
    directed_to = serializers.PrimaryKeyRelatedField(read_only=True)
    is_private = serializers.BooleanField(read_only=True)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'body')


class CommentFullSerializer(CommentSerializer):
    created_by = UserSerializer(read_only=True)
    post = PostSerializer(read_only=True)
    post_id = serializers.IntegerField(write_only=True)
    directed_to = CommentSerializer(read_only=True)
    directed_to_id = serializers.IntegerField(write_only=True, allow_null=True)

    def validate_post_id(self, value):
        if not Post.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"Post not found.")
        user = self.context['request'].user
        post = Post.objects.get(id=value)
        if not GetPostPermission.user_obj_permission(user, post):
            raise serializers.ValidationError(f"You do not have permission.")
        return value

    def validate(self, data):
        post_id = self.validate_post_id(data['post_id'])
        directed_to_id = data['directed_to_id']
        if directed_to_id is not None:
            try:
                comment = Comment.objects.get(id=directed_to_id)
            except:
                raise serializers.ValidationError(f"Comment not found.")
            if comment.post.id != post_id:
                raise serializers.ValidationError(f"post_id must be the same as the parent comment's post ID")
        return data

    class Meta(CommentSerializer.Meta):
        fields = CommentSerializer.Meta.fields + ('created_by', 'created_at', 'post', 'post_id',
                                                  'directed_to', 'directed_to_id')


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
    user = UserSerializer(read_only=True)
    post_id = serializers.IntegerField(read_only=True)
    post_type_id = serializers.IntegerField(read_only=True)

    class Meta(ReactionSerializer.Meta):
        fields = ReactionSerializer.Meta.fields + ('user', 'post_id', 'post_type_id')


class AbstractRequestSerializer(serializers.ModelSerializer):
    from_user = UserSerializer(read_only=True)

    class Meta:
        fields = ('id', 'from_user', 'sent_at', 'status', 'message')


class FriendRequestSerializer(AbstractRequestSerializer):
    to_user = UserSerializer(read_only=True)
    to_user_id = serializers.IntegerField(write_only=True)

    class Meta(AbstractRequestSerializer.Meta):
        model = FriendRequest
        fields = AbstractRequestSerializer.Meta.fields + ('to_user', 'to_user_id')


class GroupJoinRequestSerializer(AbstractRequestSerializer):
    to_group = GroupSerializer(read_only=True)
    to_group_id = serializers.IntegerField(write_only=True)

    class Meta(AbstractRequestSerializer.Meta):
        model = GroupJoinRequest
        fields = AbstractRequestSerializer.Meta.fields + ('to_group', 'to_group_id')


class GroupInviteSerializer(AbstractRequestSerializer):
    group = GroupSerializer(read_only=True)
    group_id = serializers.IntegerField(write_only=True)
    to_user = UserSerializer(read_only=True)
    to_user_id = serializers.IntegerField(write_only=True)

    class Meta(AbstractRequestSerializer.Meta):
        model = GroupInvite
        fields = AbstractRequestSerializer.Meta.fields + ('group', 'group_id', 'to_user', 'to_user_id')


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
