from rest_framework.permissions import IsAuthenticated


class IsExactUserPermission(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return request.user == obj


class FriendPermission(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return request.user in obj.friends.all() or request.user == obj


class ProfileOwnerPermission(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.user
