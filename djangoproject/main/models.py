from django.db import models

# Create your models here.

from django.db import models
from django.db.models import Q
from django.contrib.postgres.fields import ArrayField
from auth_.models import CustomUser
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from utils.constants import REACTION_TYPES, REACTION_TYPE_LIKE, REQUEST_STATUS, REQUEST_STATUS_PENDING
from utils.validators import validate_extension, validate_size
from main.permissions import GetPostPermission


class GroupManager(models.Manager):
    def get_related(self):
        return self.prefetch_related('owner', 'admins', 'members', 'posts',
                                     'sent_group_invites', 'incoming_group_join_requests')

    # def get_by_owner(self, player_id):
    #     return self.get_related().filter(id=player_id)
    #
    # def get_by_member(self, player_id):
    #     return self.get_related().filter(id=player_id)
    #
    # def get_by_post(self, player_id):
    #     return self.get_related().filter(id=player_id)
    #
    # def get_by_group_invite(self, player_id):
    #     return self.get_related().filter(id=player_id)
    #
    # def get_by_join_request(self, player_id):
    #     return self.get_related().filter(id=player_id)


class Group(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField(max_length=1000, blank=True)
    photo = models.ImageField(upload_to='group_photos',
                              validators=[validate_size, validate_extension],
                              null=True, blank=True)
    created_by_username = models.CharField(max_length=150) # will be saved even if the creator deletes
                                                           # his account or transfers ownership
    owner = models.ForeignKey(CustomUser, null=True, on_delete=models.SET_NULL,
                              related_name="owns_groups")
    created_at = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(CustomUser, related_name="member_of_groups")
    admins = models.ManyToManyField(CustomUser, related_name="admin_of_groups")

    objects = GroupManager()

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self):
        return '%s (%s)' % (self.name, self.id)

    def has_admin(self, user_id):
        return self.admins.filter(id=user_id).exists()

    def has_member(self, user_id):
        return self.members.filter(id=user_id).exists()


class ReactionManager(models.Manager):
    def get_related(self):
        return self.select_related('post_type', 'user')

    def get_by_post(self, post):
        return self.get_related().filter(post_instance=post)

    def get_by_user(self, user_id):
        return self.get_related().filter(user_id=user_id)


class Reaction(models.Model):
    post_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    post_id = models.PositiveIntegerField()
    post = GenericForeignKey('post_type', 'post_id')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="reactions")
    type = models.SmallIntegerField(choices=REACTION_TYPES, default=REACTION_TYPE_LIKE)

    objects = ReactionManager()

    class Meta:
        unique_together = ('post_id', 'post_type', 'user')
        verbose_name = "Реакция"
        verbose_name_plural = "Реакции"


class AbstractPublication(models.Model):
    body = models.TextField(max_length=5000, blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="%(class)ss")
    created_at = models.DateTimeField(auto_now_add=True)
    reactions = GenericRelation(Reaction, content_type_field='post_type', object_id_field='post_id',
                                related_query_name='%(class)s_instance')

    class Meta:
        abstract = True


class PostManager(models.Manager):
    def get_related(self):
        return self.prefetch_related('created_by', 'group', 'reactions')

    def get_by_creator(self, creator_id, request_user_id):
        """
        if request user is creator's friend or is the creator: return all non-group or group-available* posts
        else if creator is not private: return non-private and non-group or group-available* posts
        else: return only group-available* posts

        * group-available means posted to groups where both request user and creator are members
        """
        creator = CustomUser.objects.get(id=creator_id)
        req_user_groups = Group.objects.filter(members__id=request_user_id).values_list('id', flat=True)
        creator_groups = Group.objects.filter(members__id=creator_id).values_list('id', flat=True)
        common_groups = req_user_groups.filter(id__in=creator_groups)

        if creator.friends.filter(id=request_user_id).exists() or request_user_id == creator_id:
            return self.get_related().filter(Q(created_by=creator_id) &
                                             (Q(group__isnull=True) | Q(group_id__in=common_groups)))
        if not creator.is_private:
            return self.get_related().filter(Q(created_by=creator_id) &
                                             (Q(is_private=False) & Q(group__isnull=True) |
                                              Q(group_id__in=common_groups)))
        return self.get_related().filter(Q(created_by=creator_id) & Q(group_id__in=common_groups))

    def get_by_group(self, group_id):
        return self.get_related().filter(group=group_id)


class Post(AbstractPublication):
    title = models.CharField(max_length=100)
    group = models.ForeignKey(Group, on_delete=models.CASCADE,
                              blank=True, null=True)
    is_private = models.BooleanField(default=False, verbose_name="Приватность")
    image = models.ImageField(upload_to='post_images',
                              validators=[validate_size, validate_extension],
                              null=True, blank=True)

    objects = PostManager()

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"

    def get_short_title(self):
        if len(self.title) < 30:
            return self.title
        return self.title[:30] + "..."

    def __str__(self):
        return '%s (%s)' % (self.get_short_title(), self.id)


class CommentManager(models.Manager):
    def get_related(self):
        return self.prefetch_related('created_by', 'post', 'directed_to', 'reactions')

    def get_by_post(self, post_id):
        return self.get_related().filter(post=post_id)

    def get_by_parent_comment(self, comment_id):
        return self.get_related().filter(directed_to=comment_id)

    def get_by_creator(self, creator_id):
        return self.get_related().filter(created_by=creator_id)


class Comment(AbstractPublication):
    body = models.TextField(max_length=5000, blank=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    directed_to = models.ForeignKey("Comment", on_delete=models.CASCADE, related_name="replies",
                                    null=True, blank=True)

    objects = CommentManager()

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def get_short_body(self):
        if len(self.body) < 30:
            return self.body
        return self.body[:30] + "..."

    def __str__(self):
        return '%s (%s)' % (self.get_short_body(), self.id)


class AbstractRequest(models.Model):
    from_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="sent_%(class)ss")
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.SmallIntegerField(choices=REQUEST_STATUS, default=REQUEST_STATUS_PENDING)
    message = models.TextField(max_length=500, blank=True)

    class Meta:
        abstract = True


class BaseRequestManager(models.Manager):
    def get_related(self):
        # will be implemented by child managers
        pass

    def get_by_sender(self, sender):
        return self.get_related().filter(from_user=sender)


class FriendRequestManager(BaseRequestManager):
    # def create(self, from_user, sent_at, status, message, to_user, **extra_fields):
    def get_related(self):
        return self.select_related('from_user', 'to_user')

    def get_by_receiver(self, receiver):
        return self.get_related().filter(to_user=receiver)


class FriendRequest(AbstractRequest):
    to_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="incoming_friendrequests")
    objects = FriendRequestManager()

    class Meta:
        # unique_together = ('from_user', 'to_user')
        verbose_name = "Запрос на дружбу"
        verbose_name_plural = "Запросы на дружбу"


class GroupJoinRequestManager(BaseRequestManager):
    # def create(self, from_user, sent_at, status, message, to_user, **extra_fields):
    def get_related(self):
        return self.select_related('from_user', 'to_group')

    def get_by_receiver_group(self, receiver_group):
        return self.get_related().filter(to_group=receiver_group)


class GroupJoinRequest(AbstractRequest):
    to_group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="incoming_groupjoinrequests")

    objects = GroupJoinRequestManager()

    class Meta:
        # unique_together = ('from_user', 'to_group')
        verbose_name = "Запрос на присоединение к группе"
        verbose_name_plural = "Запросы на присоединение к группе"


class GroupInviteManager(BaseRequestManager):
    # def create(self, from_user, sent_at, status, message, to_user, **extra_fields):
    def get_related(self):
        return self.select_related('from_user', 'group', 'to_user')

    def get_by_receiver(self, receiver):
        return self.get_related().filter(to_user=receiver)

    def get_by_group(self, group):
        return self.get_related().filter(group=group)


class GroupInvite(AbstractRequest):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="sent_groupinvites")
    to_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="incoming_groupinvites")

    objects = GroupInviteManager()

    class Meta:
        # unique_together = ('group', 'to_user')
        verbose_name = "Приглашение в группу"
        verbose_name_plural = "Приглашения в группу"


class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Пользователь")
    text = models.TextField(max_length=500, verbose_name="Текст")
    url = models.CharField(max_length=255, blank=True, verbose_name="URL")
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False, verbose_name="Прочитано")
