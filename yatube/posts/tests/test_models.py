from django.test import TestCase

from ..models import Group, Post, User
from ..constants import MetaSet


class PostModelTest(TestCase):
    '''Класс тестирования моделей приложения posts'''
    @classmethod
    def setUpClass(cls):
        '''Фикстуры класса'''
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост' * 10,
        )

    def test_model_post_have_correct_object_name(self):
        """Проверяем, что у моделей корректно работает __str__."""
        expected_real_str = {
            PostModelTest.post.text[
                :MetaSet.MAX_CHARS_IN_TEXT_STR]: str(self.post),
            PostModelTest.group.title: str(self.group),
        }
        for expected_name, object_string in expected_real_str.items():
            with self.subTest(object_string=object_string):
                self.assertEqual(expected_name, object_string)

    def test_verbose_name_post(self):
        """verbose_name в полях модели post совпадает с ожидаемым."""
        field_verboses = {
            'text': 'содержание публикации',
            'created': 'дата создания',
            'author': 'автор публикации',
            'group': 'группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    PostModelTest.post._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_verbose_name_group(self):
        """verbose_name в полях модели group совпадает с ожидаемым."""
        field_verboses = {
            'title': 'название группы',
            'slug': 'url путь',
            'description': 'краткое описание группы',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    PostModelTest.group._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_help_text(self):
        """help_text в полях модели post совпадает с ожидаемым."""
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    PostModelTest.post._meta.get_field(field).help_text,
                    expected_value
                )
