from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    '''Информация об авторе проекта'''
    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    '''Информация о технологиях проекта'''
    template_name = 'about/tech.html'
