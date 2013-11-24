from django.core.context_processors import request
import queries
import random


def get_randomized_tags():
    popular_tags = queries.get_popular_tags()

    if popular_tags.count() == 0:
        return []

    max_count = popular_tags[0].quest_count
    min_count = popular_tags[len(popular_tags)-1].quest_count
    count_dif = max_count - min_count
    weight_count = 5

    popular_tags_list = list(popular_tags)
    random.shuffle(popular_tags_list)

    for tag in popular_tags:
        tag.weight = tag.quest_count % count_dif * weight_count / count_dif + 1

    return popular_tags_list


def tags(request):
    popular_tags_list = get_randomized_tags()

    return {
        'popular_tags': popular_tags_list,
    }


def last_registered(request):
    last_registered = queries.get_last_registered_users()

    return {
            'last_registered_left': last_registered[0:len(last_registered)/2],
            'last_registered_right': last_registered[len(last_registered)/2: len(last_registered)],
    }