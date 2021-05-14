from django.contrib import admin
from .models import Group, Post, Comment, Reaction, FriendRequest, GroupJoinRequest, GroupInvite
from django.contrib.auth.models import Group as DjangoGroup

admin.site.unregister(DjangoGroup)

admin.site.register(Group)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Reaction)
admin.site.register(FriendRequest)
admin.site.register(GroupJoinRequest)
admin.site.register(GroupInvite)
