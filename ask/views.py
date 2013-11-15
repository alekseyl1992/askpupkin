from queries import *
from django.shortcuts import *
import math

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
    page_id_str = request.GET.get('page')
    page_id = 1

    if page_id_str:
        try:
            page_id = int(page_id_str)
        except ValueError:
            return Http404

    questions_per_page = 20
    paginator_range, pages_count = get_paginator_range(Question.objects.count(), questions_per_page, page_id)

    if page == 'popular':
        questions = get_popular_questions((page_id-1)*questions_per_page, questions_per_page)
    else:
        questions = get_questions((page_id-1)*questions_per_page, questions_per_page)

    last_registered = get_last_registered_users()

    popular_tags_list = get_randomized_tags()

    for quest in questions:
        quest.short_content = quest.content[:70] + '...'

    return render(request, 'questions.html',
                  {'questions': questions,
                   'last_registered_left': last_registered[0:len(last_registered)/2],
                   'last_registered_right': last_registered[len(last_registered)/2: len(last_registered)],
                   'popular_tags': popular_tags_list,
                   'page': page,
                   'page_id': page_id,
                   'page_range': paginator_range,
                   'pages_count': pages_count}
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

    page_id_str = request.GET.get('page')
    page_id = 1

    if page_id_str:
        try:
            page_id = int(page_id_str)
        except ValueError:
            return Http404

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