from django.db import models
from django.contrib.auth.models import User


class Entry(models.Model):
    content = models.CharField(max_length=500)
    date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey('Author')

    class Meta:
        verbose_name_plural = 'entries'

    def __str__(self):
        return '{}'.format(self.content[:11])


class Comment(models.Model):
    content = models.CharField(max_length=70)
    date = models.DateTimeField(auto_now_add=True)
    entry = models.ForeignKey('Entry')
    author = models.ForeignKey('Author')

    def __str__(self):
        return '{}'.format(self.content[:11])


class Author(models.Model):
    user = models.OneToOneField(User)
    date_registered = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
