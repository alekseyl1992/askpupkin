from django.contrib.auth import authenticate, login
from django.utils.datastructures import MultiValueDictKeyError
from queries import *
from django.shortcuts import *
import math
from ask.forms import *
from django.shortcuts import *
from datetime import datetime
import json
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.exceptions import *
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render

def get_page_id(request):
    page_id_str = request.GET.get('page')

    if page_id_str:
        try:
            return int(page_id_str)
        except ValueError:
            raise Http404
    else:
        return 1


def get_paginator_range(objects_count, objects_per_page, page_id):
    page_left = 1
    page_right = 1

    pages_count = int(math.ceil(float(objects_count)/objects_per_page))

    if page_id <= 5:
        page_left = 1
    elif page_id >= pages_count - 5:
        page_left = pages_count - 9
    else:
        page_left = page_id - 4

    if page_id < 5 and pages_count >= 10:
        page_right = 10
    elif page_id < pages_count - 5:
        page_right = page_id + 5
    else:
        page_right = pages_count

    return range(page_left, page_right + 1), pages_count


def add_question(request, question_form):
    title = question_form.cleaned_data['title']
    content = question_form.cleaned_data['content']
    date = datetime.now()
    author = request.user
    rating = 0

    quest = Question(title=title, content=content, date=date, author=author, rating=rating)
    quest.save()

    for tag_name in question_form.cleaned_data['tags']:
        try:
            tag = Tag.objects.get(name__exact=tag_name)
        except Tag.DoesNotExist:
            tag = Tag(name=tag_name)
            tag.save()

        quest.tags.add(tag)

    quest.save()

    return quest.id


def question_form_view(request):
    question_form_failed = False
    question_id = None
    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        if question_form.is_valid():
            #save new question to DB
            if request.user.is_authenticated():
                question_id = add_question(request, question_form)
            else:
                raise Http404
        else:
            question_form_failed = True
    else:
        question_form = QuestionForm()

    return question_form, question_form_failed, question_id


def index(request, page):
    question_form, question_form_failed, question_id = question_form_view(request)
    if question_id is not None:
        return HttpResponseRedirect('/question/q=' + question_id)

    page_id = get_page_id(request)

    questions_per_page = 20
    paginator_range, pages_count = get_paginator_range(Question.objects.count(), questions_per_page, page_id)

    if page == 'popular':
        questions = get_popular_questions((page_id-1)*questions_per_page, questions_per_page)
    else:
        questions = get_questions((page_id-1)*questions_per_page, questions_per_page)

    #cut of one line of content
    for quest in questions:
        if len(quest.content) > 85:
            quest.short_content = quest.content[:85]
            last_space_id = quest.short_content.rfind(' ')

            if last_space_id != -1 and quest.short_content[last_space_id - 1] in [',', '.', '?']:
                last_space_id -= 1
            else:
                last_space_id = len(quest.short_content) - 1

            quest.short_content = quest.short_content[:last_space_id] + '...'
        else:
            quest.short_content = quest.content

    return render(request, 'questions.html',
                  {'questions': questions,
                   'page': page,
                   'page_id': page_id,
                   'page_range': paginator_range,
                   'pages_count': pages_count,
                   'question_form': question_form,
                   'question_form_failed': question_form_failed}
                  )


def index_latest(request):
    return index(request, 'new')


def index_popular(request):
    return index(request, 'popular')


def question(request):
    question_form, question_form_failed, question_id = question_form_view(request)
    if question_id is not None:
        return HttpResponseRedirect('/question/?q=' + str(question_id))

    question_id_str = request.GET.get('q')

    try:
        question_id = int(question_id_str)
    except (ValueError, TypeError):
        raise Http404

    answer_form_failed = False
    if request.method == 'POST':
        answer_form = AnswerForm(request.POST)
        if answer_form.is_valid():
            #add answer to db
            if request.user.is_authenticated():
                answer = Answer(question_id=question_id,
                                content=answer_form.cleaned_data['content'],
                                author=request.user,
                                date=datetime.now(),
                                rating=0)

                answer.save()
                return HttpResponseRedirect('/question/?q=' + str(question_id))
            else:
                raise Http404

        else:
            answer_form_failed = True
    else:
        answer_form = AnswerForm()

    page_id = get_page_id(request)

    quest = get_object_or_404(Question, id=question_id)

    answers_per_page = 30
    answers = get_answers(question_id, (page_id-1)*answers_per_page, answers_per_page)

    answers_count = get_answers_count(question_id)

    paginator_range, pages_count = get_paginator_range(answers_count, answers_per_page, page_id)

    return render(request, 'answers.html',
                    {'question': quest,
                     'answers': answers,
                     'page': 'question',
                     'page_id': page_id,
                     'page_range': paginator_range,
                     'pages_count': pages_count,
                     'answer_form': answer_form,
                     'answer_form_failed': answer_form_failed,
                     'question_form': question_form,
                     'question_form_failed': question_form_failed,
                    })


def tag(request):
    question_form, question_form_failed, success = question_form_view(request)
    if success is True:
        return HttpResponseRedirect('/thanks/')

    try:
        tag = request.GET['t']
    except MultiValueDictKeyError:
        raise Http404

    get_object_or_404(Tag, name__exact=tag)

    page_id = get_page_id(request)

    questions_per_page = 20

    questions = search_questions_by_tag(tag, (page_id-1)*questions_per_page, questions_per_page)
    questions_count = get_tag_question_count(tag)

    paginator_range, pages_count = get_paginator_range(questions_count, questions_per_page, page_id)

    #cut of one line of content
    for quest in questions:
        quest.short_content = quest.content[:85]
        last_space_id = quest.short_content.rfind(' ')

        if last_space_id != -1 and quest.short_content[last_space_id - 1] in [',', '.', '?']:
            last_space_id -= 1

        quest.short_content = quest.short_content[:last_space_id] + '...'

    return render(request, 'questions.html',
                  {'questions': questions,
                   'questions_count': questions_count,
                   'page': 'tag',
                   'page_id': page_id,
                   'page_range': paginator_range,
                   'pages_count': pages_count,
                   'tag': tag,
                   'question_form': question_form,
                   'question_form_failed': question_form_failed
                  })


def search(request):
    question_form, question_form_failed, success = question_form_view(request)
    if success is True:
        return HttpResponseRedirect('/thanks/')

    try:
        query = request.GET['q']
    except MultiValueDictKeyError:
        raise Http404

    questions = search_questions_by_title(query)

    page_id = get_page_id(request)

    questions_per_page = 20

    questions = search_questions_by_tag(tag, (page_id-1)*questions_per_page, questions_per_page)
    questions_count = get_tag_question_count(tag)

    paginator_range, pages_count = get_paginator_range(questions_count, questions_per_page, page_id)

    #cut of one line of content
    for quest in questions:
        quest.short_content = quest.content[:85]
        last_space_id = quest.short_content.rfind(' ')

        if last_space_id != -1 and quest.short_content[last_space_id - 1] in [',', '.', '?']:
            last_space_id -= 1

        quest.short_content = quest.short_content[:last_space_id] + '...'

    return render(request, 'questions.html',
                  {'questions': questions,
                   'questions_count': questions_count,
                   'page': 'tag',
                   'page_id': page_id,
                   'page_range': paginator_range,
                   'pages_count': pages_count,
                   'tag': tag,
                   'question_form': question_form,
                   'question_form_failed': question_form_failed
                   })


def user(request):
    question_form, question_form_failed, success = question_form_view(request)
    if success is True:
        return HttpResponseRedirect('/thanks/')

    #get user name
    try:
        name = request.GET['name']
    except MultiValueDictKeyError:
        raise Http404

    #get active tab
    try:
        tab = request.GET['tab']
    except MultiValueDictKeyError:
        tab = 'info'

    user_info = get_object_or_404(User, username__exact=name)

    asked_questions_count = get_asked_questions_count(user_info)
    answered_questions_count = get_answered_questions_count(user_info)

    if tab == 'info':
        return render(request, 'user.html',
                    {
                        'page': 'user',
                        'tab': tab,
                        'user_info': user_info,
                        'asked_questions_count': asked_questions_count,
                        'answered_questions_count': answered_questions_count,
                        'question_form': question_form,
                        'question_form_failed': question_form_failed
                    })

    elif tab == 'asked':
        questions_per_page = 20

        page_id = get_page_id(request)

        questions = get_asked_questions(user_info, (page_id-1)*questions_per_page, questions_per_page)
        questions_count = asked_questions_count

        paginator_range, pages_count = get_paginator_range(questions_count, questions_per_page, page_id)

    elif tab == 'answered':
        questions_per_page = 20

        page_id = get_page_id(request)

        questions = get_answered_questions(user_info, (page_id-1)*questions_per_page, questions_per_page)
        questions_count = answered_questions_count

        paginator_range, pages_count = get_paginator_range(questions_count, questions_per_page, page_id)

    return render(request, 'user.html',
                  {'tab': tab,
                   'user_info': user_info,
                   'questions': questions,
                   'questions_count': questions_count,
                   'asked_questions_count': asked_questions_count,
                   'answered_questions_count': answered_questions_count,
                   'page': 'user',
                   'page_id': page_id,
                   'page_range': paginator_range,
                   'pages_count': pages_count,
                   'question_form': question_form,
                   'question_form_failed': question_form_failed
                   })


def rating(request):
    try:
        id = int(request.POST['id'])
        type = request.POST['type']
        direction = request.POST['direction']
    except (MultiValueDictKeyError, ValueError):
        raise Http404

    if type == 'q':
        entry = get_object_or_404(Question, id=id)
    elif type == 'a':
        entry = get_object_or_404(Answer, id=id)
    else:
        raise Http404

    if request.user.is_authenticated():
        if not change_rating(entry, request.user, direction):
            status = "You can't vote twice."
        else:
            status = "ok"
    else:
        status = "You should login to make a vote."

    response_data = {
        'status': status,
        'rating': entry.rating
    }

    return HttpResponse(json.dumps(response_data), content_type="application/json")


def register(request):
    next = "/"

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            new_user = authenticate(username=new_user.username, password=request.POST['password1'])

            if new_user is not None:
                login(request, new_user)
                try:
                    next = request.POST['next']
                except MultiValueDictKeyError:
                    next = '/'

                return HttpResponseRedirect(next)
            else:
                raise Http404
    else:
        try:
            next = request.GET['next']
        except MultiValueDictKeyError:
            next = '/'

        form = RegistrationForm()

    return render(request, "registration/register.html", {
        'form': form,
        'next': next
    })