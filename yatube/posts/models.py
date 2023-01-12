from django.db import models
from django.contrib.auth import get_user_model

from .constants import MetaSet
from core.models import CreatedModel


User = get_user_model()


class Group(models.Model):
    '''Класс хранящий информацию о группах'''
    title = models.CharField('название группы', max_length=200)
    slug = models.SlugField('url путь', unique=True)
    description = models.TextField('краткое описание группы')

    class Meta:
        verbose_name = 'группа'
        verbose_name_plural = 'группы'

    def __str__(self):
        '''Вывод названия группы'''

        return self.title


class Post(CreatedModel):
    '''Класс хранящий информацию о постах'''
    text = models.TextField('содержание публикации',
                            help_text='Введите текст поста')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='автор публикации'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='group',
        verbose_name='группа',
        help_text='Группа, к которой будет относиться пост'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
        help_text='Добавьте изображение к посту'
    )

    class Meta:
        ordering = ['-created']
        verbose_name = 'пост'
        verbose_name_plural = 'посты'

    def __str__(self) -> str:
        '''Вывод текста поста'''

        return self.text[:MetaSet.MAX_CHARS_IN_TEXT_STR]


class Comment(CreatedModel):
    '''Класс коментариев к постам'''
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        blank=True,
        related_name='comments',
        verbose_name='пост',
        help_text='Пост к которому относится коментарий'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='автор коментария',
        help_text='Автор, написавший коментарий'
    )
    text = models.TextField(
        'текст коментария',
        help_text='Введите текст коментария'
    )

    class Meta:
        ordering = ['-created']
        verbose_name = 'коментарий'
        verbose_name_plural = 'коментарии'

    def __str__(self) -> str:
        '''Вывод текста коментария'''

        return self.text[:MetaSet.MAX_CHARS_IN_TEXT_STR]


class Follow(CreatedModel):
    '''Класс подписки на авторов'''
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='подписчик',
        help_text='Пользоваетль, который подписывается на автора'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='автор',
        help_text='Автор, на которого подписываются'
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'

    def __str__(self) -> str:
        '''Вывод текста коментария'''

        return (
            self.user.get_username() + ' fllow: ' + self.author.get_username())
