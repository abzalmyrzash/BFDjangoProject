from django.db import models

# Create your models here.

from django.db import models
from django.contrib.postgres.fields import ArrayField


class Group(models.Model):
    name = models.CharField(max_length=30)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=0, related_name="created_groups")
    created_at = models.DateTimeField(auto_now_add=True)
    subscribers = models.ManyToManyField(CustomUser, related_name="subscribed_groups")


class Post(models.Model):
    title = models.CharField(max_length=100)
    body = models.CharField(max_length=1000, default='')
    likes = models.ManyToManyField(CustomUser, related_name="liked_posts")
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE,
                              blank=True, null=True)


class Comment(models.Model):
    body = models.CharField(max_length=1000, default='')
    likes = models.ManyToManyField(CustomUser, related_name="liked_comments")
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments",
                             blank=True, null=True)
    directed_to = models.ForeignKey("Comment", on_delete=models.CASCADE, related_name="replies",
                                    blank=True, null=True)
