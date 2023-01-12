import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.shortcuts import get_object_or_404

from ..models import Post, Group, User


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        '''Фикстуры класса'''
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        '''Фикстуры'''
        self.authorized_autor = Client()
        self.authorized_autor.force_login(PostCreateFormTest.user)

    def test_post_creation_form(self):
        '''Проверка создания новой записи в базе данных'''
        all_posts_id_before_creating = [post.id for post in Post.objects.all()]
        byte_image = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.image = SimpleUploadedFile(
            name='test_image.gif',
            content=byte_image,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Совершенно новый пост',
            'group': PostCreateFormTest.group.id,
            'image': self.image,
        }
        response = self.authorized_autor.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True)
        new_post_set = Post.objects.exclude(
            id__in=all_posts_id_before_creating)
        self.assertEqual(new_post_set.count(), 1)
        print(self.image)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                author=PostCreateFormTest.user,
                image=Post.image.field.upload_to + self.image.name
            ).exists()
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': PostCreateFormTest.user.username}))

    def test_post_edit_form(self):
        '''Проверка формы редактированиия поста'''
        posts_amount_before_editing = Post.objects.count()
        form_data = {
            'text': 'Редактированный текст',
            'group': PostCreateFormTest.group.id
        }
        self.authorized_autor.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostCreateFormTest.post.id}
            ),
            data=form_data,
            follow=True
        )
        posts_amount_after_editing = Post.objects.count()
        edited_post = get_object_or_404(Post, id=PostCreateFormTest.post.id)
        self.assertEqual(
            posts_amount_before_editing,
            posts_amount_after_editing
        )
        self.assertEqual(
            form_data['text'],
            edited_post.text
        )
        self.assertEqual(
            form_data['group'],
            edited_post.id
        )
        self.assertEqual(
            self.user,
            edited_post.author
        )
