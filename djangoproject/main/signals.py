from django.db.models.signals import post_save
from django.dispatch import receiver
from main.models import FriendRequest, GroupJoinRequest, GroupInvite, Reaction, Comment, Notification
from utils.constants import REACTION_COUNT_MILESTONES


@receiver(post_save, sender=FriendRequest)
def friend_request_created(sender, instance, created, **kwargs):
    if created:
        from_user = instance.from_user
        to_user = instance.to_user
        text = f"{from_user.profile.get_full_name()} wants to be your friend!"
        Notification.objects.create(user=to_user, text=text)


@receiver(post_save, sender=GroupJoinRequest)
def group_join_request_created(sender, instance, created, **kwargs):
    if created:
        from_user = instance.from_user
        group = instance.to_group
        for admin in group.admins.all():
            text = f"{from_user.profile.get_full_name()} wants to join your group {group}!"
            Notification.objects.create(user=admin, text=text)


@receiver(post_save, sender=GroupInvite)
def group_invite_created(sender, instance, created, **kwargs):
    if created:
        from_user = instance.from_user
        to_user = instance.to_user
        group = instance.group

        text = f"{from_user.profile.get_full_name()} invited you to join their group {group}!"
        Notification.objects.create(user=to_user, text=text)


@receiver(post_save, sender=Reaction)
def reaction_created(sender, instance, created, **kwargs):
    if created:
        post = instance.post
        # reaction_count = Reaction.objects.get_by_post(post_id=post.id).count()
        reaction_count = post.reactions.count()
        if reaction_count in REACTION_COUNT_MILESTONES:
            post_type = post.__class__.__name__.lower()
            user = post.created_by
            person_or_people = "person has" if reaction_count == 1 else "people have"
            text = f"{reaction_count} {person_or_people} reacted to your {post_type} \"{post.get_short_title()}\"!"
            Notification.objects.create(user=user, text=text)


@receiver(post_save, sender=Comment)
def comment_created(sender, instance, created, **kwargs):
    if created:
        commenter = instance.created_by
        post = instance.post
        comment = instance.directed_to

        if comment is None:
            user = post.created_by
            text = f"{commenter.profile.get_full_name()} has commented on your post \"{post.get_short_title()}\"!"
            Notification.objects.create(user=user, text=text)
        else:
            user = comment.created_by
            text = f"{commenter.profile.get_full_name()} has replied to your comment \"{comment.get_short_body()}\"!"
            Notification.objects.create(user=user, text=text)