from django.db import models

# Create your models here.

from django.db import models
from django.contrib.postgres.fields import ArrayField
from auth_.models import CustomUser
from utils.constants import REACTION_TYPES, REACTION_TYPE_LIKE, REQUEST_STATUS, REQUEST_STATUS_PENDING


class Group(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField(max_length=1000)
    owner = models.ForeignKey(CustomUser, null=True, on_delete=models.SET_NULL,
                              related_name="created_groups")
    created_at = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(CustomUser, related_name="member_groups")
    admins = models.ManyToManyField(CustomUser, related_name="admin_groups")

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"


class AbstractPost(models.Model):
    body = models.TextField(max_length=5000, blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Post(AbstractPost):
    title = models.CharField(max_length=100)
    group = models.ForeignKey(Group, on_delete=models.CASCADE,
                              blank=True, null=True)
    is_private = models.BooleanField(default=False, verbose_name="Приватность")

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"


class Comment(AbstractPost):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments",
                             blank=True, null=True)
    directed_to = models.ForeignKey("Comment", on_delete=models.CASCADE, related_name="replies",
                                    blank=True, null=True)

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"


class Reaction(models.Model):
    post = models.ForeignKey(AbstractPost, related_name="reactions")
    user = models.ForeignKey(CustomUser, related_name="reactions")
    type = models.SmallIntegerField(choices=REACTION_TYPES, default=REACTION_TYPE_LIKE)

    class Meta:
        verbose_name = "Реакция"
        verbose_name_plural = "Реакции"


class AbstractRequest(models.Model):
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.SmallIntegerField(choices=REQUEST_STATUS, default=REQUEST_STATUS_PENDING)
    message = models.TextField

    class Meta:
        abstract = True


class FriendRequest(AbstractRequest):
    from_user = models.ForeignKey(CustomUser, related_name="sent_friend_requests")
    to_user = models.ForeignKey(CustomUser, related_name="incoming_friend_requests")

    class Meta:
        verbose_name = "Запрос на дружбу"
        verbose_name_plural = "Запросы на дружбу"


class GroupJoinRequest(AbstractRequest):
    from_user = models.ForeignKey(CustomUser, related_name="sent_join_requests")
    to_group = models.ForeignKey(Group, related_name="incoming_join_requests")

    class Meta:
        verbose_name = "Запрос на присоединение к группе"
        verbose_name_plural = "Запросы на присоединение к группе"


class GroupInvite(AbstractRequest):
    from_user = models.ForeignKey(CustomUser, related_name="sent_invites")
    to_user = models.ForeignKey(CustomUser, related_name="incoming_invites")

    class Meta:
        verbose_name = "Приглашение в группу"
        verbose_name_plural = "Приглашения в группу"
