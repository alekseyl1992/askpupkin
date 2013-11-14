from queries import *
from django.shortcuts import *
import math

def index(request, page):
    page_id_str = request.GET.get('page')
    page_id = 1

    if page_id_str:
        try:
            page_id = int(page_id_str)
        except ValueError:
            return Http404

    page_left = 1
    page_right = 1

    questions_per_page = 30

    pages_count = int(math.ceil(float(Question.objects.count())/questions_per_page))

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

    if page == 'popular':
        questions = get_popular_questions((page_id-1)*questions_per_page, questions_per_page)
    else:
        questions = get_questions((page_id-1)*questions_per_page, questions_per_page)

    last_registered = get_last_registered_users()
    popular_tags = get_popular_tags()

    max_count = popular_tags[0].quest_count
    min_count = popular_tags[len(popular_tags)-1].quest_count
    count_dif = max_count - min_count
    weight_count = 5

    popular_tags_list = list(popular_tags)
    random.shuffle(popular_tags_list)

    for tag in popular_tags:
        tag.weight = tag.quest_count % count_dif * weight_count / count_dif + 1

    return render(request, 'index.html',
                  {'questions': questions,
                   'last_registered_left': last_registered[0:len(last_registered)/2],
                   'last_registered_right': last_registered[len(last_registered)/2: len(last_registered)],
                   'popular_tags': popular_tags_list,
                   'page': page,
                   'page_id': page_id,
                   'page_range': range(page_left, page_right + 1),
                   'pages_count': pages_count}
                  )


def index_latest(request):
    return index(request, 'new')


def index_popular(request):
    return index(request, 'popular')
