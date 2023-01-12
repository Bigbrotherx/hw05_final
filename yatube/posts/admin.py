from django.contrib import admin

from .models import Post, Group


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    '''Класс конфигурации модели Post в админке'''
    list_display = (
        'pk',
        'text',
        'created',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('created',)
    empty_value_display = '-пусто-'


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    '''Класс конфигурации модели Group в админке'''
    list_display = (
        'pk',
        'title',
        'slug',
        'description',
    )
    list_editable = ('description',)
    search_fields = ('title', 'slug',)
    empty_value_display = '-пусто-'
