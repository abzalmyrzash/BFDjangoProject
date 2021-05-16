from rest_framework.permissions import IsAuthenticated, BasePermission
from auth_.permissions import FriendPermission

"""
NOTE:
I implemented a separate static function user_obj_permission(user, obj) for each permission class
so I can use permissions without passing request and view as arguments, especially in model managers
"""


class GroupMemberPermission(IsAuthenticated):
    @staticmethod
    def user_obj_permission(user, obj):
        return user in obj.members.all()

    def has_object_permission(self, request, view, obj):
        return self.user_obj_permission(request.user, obj)


class GroupAdminPermission(IsAuthenticated):
    @staticmethod
    def user_obj_permission(user, obj):
        return user in obj.admins.all()

    def has_object_permission(self, request, view, obj):
        return self.user_obj_permission(request.user, obj)


class GroupOwnerPermission(IsAuthenticated):
    @staticmethod
    def user_obj_permission(user, obj):
        return user == obj.owner

    def has_object_permission(self, request, view, obj):
        return self.user_obj_permission(request.user, obj)


class PostCommentCreatorPermission(IsAuthenticated):
    @staticmethod
    def user_obj_permission(user, obj):
        return user == obj.created_by

    def has_object_permission(self, request, view, obj):
        return self.user_obj_permission(request.user, obj)


class GetPostPermission(BasePermission):
    @staticmethod
    def user_obj_permission(user, obj):
        if obj.created_by == user:
            return True
        if obj.group is not None:
            return GroupMemberPermission.user_obj_permission(user, obj.group)
        if not (obj.is_private or obj.created_by.is_private):
            return True
        return FriendPermission.user_obj_permission(user, obj.created_by)

    def has_object_permission(self, request, view, obj):
        return self.user_obj_permission(request.user, obj)


class GetCommentPermission(BasePermission):
    @staticmethod
    def user_obj_permission(user, obj):
        return PostCommentCreatorPermission.user_obj_permission(user, obj.post) or obj.created_by == user

    def has_object_permission(self, request, view, obj):
        return self.user_obj_permission(request.user, obj)
