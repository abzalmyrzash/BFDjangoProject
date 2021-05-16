from rest_framework.permissions import IsAuthenticated

"""
NOTE:
I implemented a separate static function user_obj_permission(user, obj) for each permission class
so I can use permissions without passing request and view as arguments, especially in model managers
"""


class IsExactUserPermission(IsAuthenticated):
    @staticmethod
    def user_obj_permission(user, obj):
        return user == obj

    def has_object_permission(self, request, view, obj):
        return self.user_obj_permission(request.user, obj)


class FriendPermission(IsAuthenticated):
    @staticmethod
    def user_obj_permission(user, obj):
        return user in obj.friends.all() or user == obj

    def has_object_permission(self, request, view, obj):
        return self.user_obj_permission(request.user, obj)


class ProfileOwnerPermission(IsAuthenticated):
    @staticmethod
    def user_obj_permission(user, obj):
        return user == obj.user

    def has_object_permission(self, request, view, obj):
        return self.user_obj_permission(request.user, obj)
