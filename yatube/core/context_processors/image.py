import re

from django.urls import reverse


def image(request):
    '''Добавляет картинку в шапку старницы'''
    if request.get_full_path() == reverse('posts:index'):
        return {
            'image': 'url(/static/img/home-bg.jpg)'
        }
    elif request.get_full_path() == reverse('posts:follow_index'):
        return {
            'image': 'url(/static/img/home-bg.jpg)'
        }
    elif request.get_full_path() == reverse('about:author'):
        return {
            'image': 'url(/static/img/about-bg.jpg)'
        }
    elif request.get_full_path() == reverse('about:tech'):
        return {
            'image': 'url(/static/img/tech-bg.jpg)'
        }
    elif re.search(r'profile/', request.get_full_path()):
        return {
            'image': 'url(/static/img/contact-bg.jpg)'
        }
    elif re.search(r'posts/\d', request.get_full_path()):
        return {
            'image': 'url(/static/img/edit-bg.jpg)'
        }
    elif re.search(r'group/\w', request.get_full_path()):
        return {
            'image': 'url(/static/img/group-bg.jpg)'
        }
    elif request.get_full_path() == reverse('users:login'):
        return {
            'image': 'url(/static/img/login-bg.jpg)'
        }
    elif request.get_full_path() == reverse('users:signup'):
        return {
            'image': 'url(/static/img/login-bg.jpg)'
        }
    return {
    }
