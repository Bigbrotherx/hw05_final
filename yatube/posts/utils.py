from django.core.paginator import Paginator

from .constants import PageSet


def add_paginator(request, posts):
    '''Функция добавления пагинатора при отображении постов'''
    paginator = Paginator(posts, PageSet.POSTS_AMOUNT_AT_PADGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return page_obj
