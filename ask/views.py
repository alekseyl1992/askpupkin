from django.utils.datastructures import MultiValueDictKeyError
from queries import *
from django.shortcuts import *
import math
from ask.forms import *

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


def get_randomized_tags():
    popular_tags = get_popular_tags()

    max_count = popular_tags[0].quest_count
    min_count = popular_tags[len(popular_tags)-1].quest_count
    count_dif = max_count - min_count
    weight_count = 5

    popular_tags_list = list(popular_tags)
    random.shuffle(popular_tags_list)

    for tag in popular_tags:
        tag.weight = tag.quest_count % count_dif * weight_count / count_dif + 1

    return popular_tags_list


def index(request, page):
    question_form_failed = False
    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        if question_form.is_valid():
            return HttpResponseRedirect('/thanks/')
        else:
            question_form_failed = True
    else:
        question_form = QuestionForm()

    page_id = get_page_id(request)

    questions_per_page = 20
    paginator_range, pages_count = get_paginator_range(Question.objects.count(), questions_per_page, page_id)

    if page == 'popular':
        questions = get_popular_questions((page_id-1)*questions_per_page, questions_per_page)
    else:
        questions = get_questions((page_id-1)*questions_per_page, questions_per_page)

    last_registered = get_last_registered_users()

    popular_tags_list = get_randomized_tags()

    #cut of one line of content
    for quest in questions:
        quest.short_content = quest.content[:85]
        last_space_id = quest.short_content.rfind(' ')

        if last_space_id != -1 and quest.short_content[last_space_id - 1] in [',', '.', '?']:
            last_space_id -= 1

        quest.short_content = quest.short_content[:last_space_id] + '...'

    return render(request, 'questions.html',
                  {'questions': questions,
                   'last_registered_left': last_registered[0:len(last_registered)/2],
                   'last_registered_right': last_registered[len(last_registered)/2: len(last_registered)],
                   'popular_tags': popular_tags_list,
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
    question_id_str = request.GET.get('q')

    try:
        question_id = int(question_id_str)
    except ValueError:
        return Http404

    page_id = get_page_id(request)

    quest = get_question(question_id)

    answers_per_page = 30
    answers = get_answers(question_id, (page_id-1)*answers_per_page, answers_per_page)

    answers_count = get_answers_count(question_id)

    paginator_range, pages_count = get_paginator_range(answers_count, answers_per_page, page_id)

    last_registered = get_last_registered_users()
    popular_tags_list = get_randomized_tags()

    return render(request, 'answers.html',
              {'question': quest,
               'answers': answers,
               'last_registered_left': last_registered[0:len(last_registered)/2],
               'last_registered_right': last_registered[len(last_registered)/2: len(last_registered)],
               'popular_tags': popular_tags_list,
               'page': 'question',
               'page_id': page_id,
               'page_range': paginator_range,
               'pages_count': pages_count}
              )


def tag(request):
    try:
        tag = request.GET['t']
    except MultiValueDictKeyError:
        return Http404

    page_id = get_page_id(request)

    questions_per_page = 20

    questions = search_questions_by_tag(tag, (page_id-1)*questions_per_page, questions_per_page)
    questions_count = get_tag_question_count(tag)

    paginator_range, pages_count = get_paginator_range(questions_count, questions_per_page, page_id)

    last_registered = get_last_registered_users()

    popular_tags_list = get_randomized_tags()

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
                   'last_registered_left': last_registered[0:len(last_registered)/2],
                   'last_registered_right': last_registered[len(last_registered)/2: len(last_registered)],
                   'popular_tags': popular_tags_list,
                   'page': 'tag',
                   'page_id': page_id,
                   'page_range': paginator_range,
                   'pages_count': pages_count,
                   'tag': tag}
                  )


def user(request):
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

    user = User.objects.get(username__exact=name)

    last_registered = get_last_registered_users()

    popular_tags_list = get_randomized_tags()

    asked_questions_count = get_asked_questions_count(user)
    answered_questions_count = get_answered_questions_count(user)

    if tab == 'info':
        return render(request, 'user.html',
                    {
                        'page': 'user',
                        'tab': tab,
                        'user': user,
                        'asked_questions_count': asked_questions_count,
                        'answered_questions_count': answered_questions_count,
                        'last_registered_left': last_registered[0:len(last_registered)/2],
                        'last_registered_right': last_registered[len(last_registered)/2: len(last_registered)],
                        'popular_tags': popular_tags_list,
                    })

    elif tab == 'asked':
        questions_per_page = 20

        page_id = get_page_id(request)

        questions = get_asked_questions(user, (page_id-1)*questions_per_page, questions_per_page)
        questions_count = asked_questions_count

        paginator_range, pages_count = get_paginator_range(questions_count, questions_per_page, page_id)

    elif tab == 'answered':
        questions_per_page = 20

        page_id = get_page_id(request)

        questions = get_answered_questions(user, (page_id-1)*questions_per_page, questions_per_page)
        print questions
        questions_count = answered_questions_count

        paginator_range, pages_count = get_paginator_range(questions_count, questions_per_page, page_id)

    return render(request, 'user.html',
              {'tab': tab,
               'user': user,
               'questions': questions,
               'questions_count': questions_count,
               'asked_questions_count': asked_questions_count,
               'answered_questions_count': answered_questions_count,
               'last_registered_left': last_registered[0:len(last_registered)/2],
               'last_registered_right': last_registered[len(last_registered)/2: len(last_registered)],
               'popular_tags': popular_tags_list,
               'page': 'user',
               'page_id': page_id,
               'page_range': paginator_range,
               'pages_count': pages_count}
              )
