from django.core.paginator import Paginator

NUMBER_OF_POSTS: int = 3


def get_paginator(request, argument):
    paginator = Paginator(argument, NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'page_obj': page_obj
    }
