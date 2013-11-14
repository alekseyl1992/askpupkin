import sys, os
sys.path.append('/home/alekseyl/askpupkin/askpupkin')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from django.conf import settings
from ask.models import *
from django.contrib.auth.models import User
import random

from random_words import *


def has_user(username):
    if len(User.objects.filter(username__exact=username)):
        return True

    return False


def has_tag(tags, tagname):
    for t in tags:
        if t.name == tagname:
            return True

    return False

rw = RandomWords()
re = RandomEmails()
rn = RandomNicknames()
rc = LoremIpsum()

tags = []

for i in range(0, 100):
    tagname = rw.random_word()
    while has_tag(tags, tagname):
        tagname = rw.random_word()

    tag = Tag(name=tagname)
    tag.save()
    tags.append(tag)

print "Tags added"

user_ids = []

for i in range(0, 10000):
    username = rn.random_nick(gender='u')

    while has_user(username):
        username = rn.random_nick(gender='u') + str(random.randint(10, 999))

    user = User.objects.create_user(username=username, email=re.randomMail(), password=rw.random_word())
    user.save()
    user_ids.append(user.id)

print "Users added"

question_ids = []

for i in range(0, 100000):
    title = rc.get_sentence()
    if len(title) > 100:
        title = title[0:99]
    q_title = title[0:len(title)-1]

    quest = Question(title=q_title+"?", author_id=user_ids[random.randint(0, len(user_ids)-1)],
                     rating=random.randint(0, 999), content=rc.get_sentences(random.randint(5, 10)))

    quest.save()

    for j in range(0, random.randint(0, 3)):
        quest.tags.add(tags[random.randint(0, len(tags)-1)])

    quest.save()

    question_ids.append(quest.id)

print "Questions added"

for i in range(0, 1000000):
    answer = Answer(author_id=user_ids[random.randint(0, len(user_ids)-1)],
                    question_id=question_ids[random.randint(0, len(question_ids)-1)],
                    right=random.choice([False, True, False, False, False]),
                    content=rc.get_sentences(random.randint(1, 5)))

    answer.save()

print "Answers added"