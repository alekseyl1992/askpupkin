 # -*- coding: utf8 -*-

import sys, os
sys.path.append('/home/alekseyl/askpupkin/askpupkin')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from django.conf import settings
from ask.models import *
from django.contrib.auth.models import User
import random
from django.db.models import Count


from random_words import *


def get_questions(offset, count=30):
    return Question.objects.order_by('-date')[offset:offset+count]


def get_popular_questions(offset, count=30):
    return Question.objects.order_by('-rating')[offset:offset+count]


def get_answers(question_id, offset, count=30):
    return Answer.objects.filter(question_id=question_id)[offset:offset+count]


def search_questions_by_tag(tag_name, offset, count=30):
    return Question.objects.filter(tags__name=tag_name)[offset:offset+count]


def search_questions_by_title(title, offset, count=30):
    return Question.objects.filter(title__icontains=title)[offset:offset+count]


def search_questions_by_content(content, offset, count=30):
    return Question.objects.filter(content__icontains=content)[offset:offset+count]


def get_popular_tags():
    return Tag.objects.annotate(quest_count=Count('question')).order_by('-quest_count')[0:25]


def get_answers_count(question_id):
    return Answer.objects.filter(question_id=question_id).count()


def get_question_rating(question_id):
    return QuestionVote.objects.filter(question_id=question_id).aggregate(models.Sum('value'))


def get_answer_rating(answer_id):
    return AnswerVote.objects.filter(answer_id=answer_id).aggregate(models.Sum('value'))


def get_last_registered_users():
    return User.objects.order_by('-date_joined')[0:10]


def get_tag_question_count(tag_name):
    return Question.objects.filter(tags__name=tag_name).count()


def get_asked_questions(user, offset, count=20):
    return Question.objects.filter(author=user)[offset:offset+count]


def get_asked_questions_count(user):
    return Question.objects.filter(author=user).count()


def get_answered_questions(user, offset, count=20):
    answers = Answer.objects.filter(author=user).order_by('question').distinct()[offset:offset+count]
    questions = []

    for ans in answers:
        questions.append(ans.question)

    return questions


def get_answered_questions_count(user):
    return Answer.objects.filter(author=user).order_by('question').distinct().count()

