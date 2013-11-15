from django.db import models
from django.contrib.auth.models import User


class Tag(models.Model):
    name = models.CharField(max_length=32, db_index=True)


class Question(models.Model):
    title = models.CharField(max_length=100)
    content = models.CharField(max_length=2048)
    author = models.ForeignKey(User)
    date = models.DateTimeField()
    tags = models.ManyToManyField(Tag)
    rating = models.IntegerField()


class Answer(models.Model):
    content = models.CharField(max_length=1024)
    question = models.ForeignKey(Question)
    author = models.ForeignKey(User)
    date = models.DateTimeField()
    right = models.BooleanField()
    rating = models.IntegerField()


class QuestionVote(models.Model):
    question = models.ForeignKey(Question)
    user = models.ForeignKey(User)
    value = models.SmallIntegerField()


class AnswerVote(models.Model):
    answer = models.ForeignKey(Answer)
    user = models.ForeignKey(User)
    value = models.SmallIntegerField()