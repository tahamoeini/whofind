from tkinter import CASCADE
import uuid
from django.db import models


class Keywords(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    text = models.CharField(max_length=1024)


class Link(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    link = models.URLField(max_length=1024, unique=True)
    domain = models.CharField(max_length=1024)
    description = models.TextField()
    title = models.CharField(max_length=512)


class LinkPosition(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    queryKeyword = models.ForeignKey(Keywords, on_delete=models.CASCADE)
    link = models.ForeignKey(Link, on_delete=models.CASCADE)
    position = models.IntegerField()


class RelatedKeywords(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    queryKeyword = models.OneToOneField(
        Keywords, on_delete=models.CASCADE, unique=True, related_name="relatedKeywords")
    relatedKeywords = models.ManyToManyField(
        Keywords, related_name="parentKeyword")
