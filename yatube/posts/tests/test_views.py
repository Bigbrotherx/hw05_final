import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.cache import cache

from ..models import Post, Group, Comment, Follow, User
from ..forms import PostForm, CommentForm
from ..constants import PageSet


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTest(TestCase):
    '''Класс тестов view функций и классов приложения post'''
    @classmethod
    def setUpClass(cls):
        '''Фикстуры класса'''
        super().setUpClass()
        byte_image = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.image = SimpleUploadedFile(
            name='test_image.gif',
            content=byte_image,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='author')
        cls.follower = User.objects.create_user(username='follower')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.another_group = Group.objects.create(
            title='Группа без постов',
            slug='out-of-posts',
            description='Описание',
        )
        Post.objects.bulk_create([
            Post(
                text='Тестовый пост' + str(index),
                author=cls.user,
                group=cls.group,
                image=cls.image,
            )for index in reversed(range(
                PageSet.POSTS_AMOUNT_AT_PADGE
                + PageSet.ADITIONAL_POSTS_FOR_TEST
            ))
        ])
        cls.posts = Post.objects.all()
        cls.post_with_comment = Post.objects.first()
        cls.comment = Comment.objects.create(
            post=cls.post_with_comment,
            author=cls.follower,
            text='Тестовый коммент',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        '''Фикстуры'''
        self.authorized_author = Client()
        self.authorized_author.force_login(PostViewsTest.user)
        self.follower = Client()
        self.follower.force_login(PostViewsTest.follower)
        self.follower.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': PostViewsTest.user.username}
            ),
        )
        self.pages_with_paginator = [
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': PostViewsTest.group.slug}),
            reverse('posts:profile',
                    kwargs={'username': PostViewsTest.user.username}),
        ]

    def check_post_context(self, post):
        self.assertEqual(post.id, PostViewsTest.posts[0].id)
        self.assertEqual(post.text, PostViewsTest.posts[0].text)
        self.assertEqual(post.group, PostViewsTest.posts[0].group)
        self.assertEqual(post.author, PostViewsTest.posts[0].author)
        self.assertEqual(post.image, PostViewsTest.posts[0].image)

    def test_pages_uses_correct_templates(self):
        '''Проверка namspace post на корректность шаблонов'''
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': PostViewsTest.group.slug}
                    ): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': PostViewsTest.user.username}
                    ): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': PostViewsTest.posts[0].id}
                    ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': PostViewsTest.posts[0].id}
                    ): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_shows_correct_context(self):
        '''Проверка контекста главной страницы'''
        response = self.authorized_author.get(
            reverse('posts:index')
        )
        self.check_post_context(response.context['page_obj'][0])

    def test_group_list_shows_correct_context(self):
        '''Проверка контекста страницы группы'''
        response = self.authorized_author.get(
            reverse('posts:group_list',
                    kwargs={'slug': PostViewsTest.group.slug})
        )
        self.assertEqual(response.context['group'], PostViewsTest.group)
        self.check_post_context(response.context['page_obj'][0])

    def test_profile_shows_correct_context(self):
        '''Проверка контекста страницы профиля'''
        response = self.follower.get(
            reverse('posts:profile',
                    kwargs={'username': PostViewsTest.user.username})
        )
        self.assertEqual(response.context['author'], PostViewsTest.user)
        self.assertTrue(response.context['following'])
        self.check_post_context(response.context['page_obj'][0])

    def test_post_detail_context(self):
        '''Проверка контекста индивидуальной страницы поста'''
        response = self.authorized_author.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': PostViewsTest.posts[0].id}))
        self.check_post_context(response.context['post'])
        self.assertIsInstance(response.context['form'], CommentForm)
        self.assertEqual(
            response.context['comments'][0],
            PostViewsTest.comment
        )

    def test_first_page_contains_correct_amount_of_records(self):
        '''Проверка корректное количество постов на первой странице'''
        for page in self.pages_with_paginator:
            with self.subTest(page=page):
                response = self.authorized_author.get(page)
                self.assertEqual(
                    len(response.context['page_obj']),
                    PageSet.POSTS_AMOUNT_AT_PADGE)

    def test_second_page_contains_one_record(self):
        '''Провека корректное количество постов на второй странице'''
        for page in self.pages_with_paginator:
            with self.subTest(page=page):
                response = self.client.get(page + '?page=2')
                self.assertEqual(
                    len(response.context['page_obj']),
                    PageSet.ADITIONAL_POSTS_FOR_TEST
                )

    def test_edit_post_context(self):
        '''Проверка контекста формы редактирования поста'''
        response = self.authorized_author.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': PostViewsTest.posts[5].id}))
        self.assertIsInstance(response.context['form'], PostForm)
        self.assertEqual(response.context['is_edit'], True)
        self.assertEqual(
            response.context['post_id'], PostViewsTest.posts[5].id
        )

    def test_create_post_context(self):
        '''Проверка контекста формы создания поста'''
        response = self.authorized_author.get(reverse('posts:post_create'))
        self.assertIsInstance(response.context['form'], PostForm)

    def test_another_group_without_posts(self):
        '''Проверка что пост не попал в другую группу'''
        response = self.authorized_author.get(
            reverse('posts:group_list',
                    kwargs={'slug': PostViewsTest.another_group.slug})
        )
        all_posts_of_group = response.context['page_obj'].object_list
        self.assertEqual(len(all_posts_of_group), 0)

    def test_new_post_at_first_place(self):
        '''Проверка что новый пост попадает на первое место'''
        new_post = Post.objects.create(
            text='Новый пост',
            group=PostViewsTest.group,
            author=PostViewsTest.user,
        )
        for page in self.pages_with_paginator:
            with self.subTest(page=page):
                first_post_at_page = self.authorized_author.get(
                    page
                ).context['page_obj'][0]
                self.assertEqual(new_post, first_post_at_page)

    def test_cache_index(self):
        """Проверка хранения и очищения кэша для index."""
        response = self.authorized_author.get(reverse('posts:index'))
        Post.objects.create(
            text='Новый пост',
            group=PostViewsTest.group,
            author=PostViewsTest.user,
        )
        response_old = self.authorized_author.get(reverse('posts:index'))
        self.assertEqual(response.content, response_old.content)
        cache.clear()
        response_new = self.authorized_author.get(reverse('posts:index'))
        self.assertNotEqual(response_old.content, response_new.content)

    def test_new_post_at_follower_page(self):
        '''Проверка что новый пост появляется у подписчиков'''
        new_post = Post.objects.create(
            text='Новый пост',
            group=PostViewsTest.group,
            author=PostViewsTest.user,
        )
        favorite_page = self.follower.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(new_post, favorite_page.context['page_obj'][0])

    def test_new_post_at_not_a_follower_page(self):
        '''Проверка что новый пост не появляется у тех кто не подписан'''
        Post.objects.create(
            text='Новый пост',
            group=PostViewsTest.group,
            author=PostViewsTest.user,
        )
        favorite_page = self.authorized_author.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(0, len(favorite_page.context['page_obj']))

    def test_start_following(self):
        '''Проверка возможности подписаться на автора'''
        self.new_user = User.objects.create_user(username='new_follower')
        self.new_follower = Client()
        self.new_follower.force_login(self.new_user)
        self.new_follower.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': PostViewsTest.user}
            )
        )
        self.assertTrue(Follow.objects.filter(
            author=PostViewsTest.user,
            user=self.new_user
        ).exists())

    def test_stop_following(self):
        '''Проверка возможности отписаться от автора'''
        self.follower.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': PostViewsTest.user}
            )
        )
        self.assertFalse(Follow.objects.filter(
            author=PostViewsTest.user,
            user=PostViewsTest.follower
        ).exists())
