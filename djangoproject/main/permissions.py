from rest_framework.permissions import IsAuthenticated, BasePermission
from auth_.permissions import FriendPermission


class GroupMemberPermission(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return request.user in obj.members.all()


class GroupAdminPermission(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return request.user in obj.admins.all()


class GroupOwnerPermission(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner


class PostCreatorPermission(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.created_by


class GetPostPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.created_by == request.user:
            return True
        if obj.group is not None:
            return GroupMemberPermission().has_object_permission(request, view, obj.group)
        if not (obj.is_private or obj.created_by.is_private):
            return True
        return FriendPermission().has_object_permission(request, view, obj.created_by)
