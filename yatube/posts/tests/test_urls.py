from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from ..models import Group, Post, User


class StaticURLTests(TestCase):
    '''Класс тестов доступности url адресов'''
    @classmethod
    def setUpClass(cls):
        '''Фикстуры класса'''
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
        )

    def setUp(self):
        '''Фикстуры класса'''
        self.authorized_client = Client()
        self.authorized_author = Client()
        self.authorized_client.force_login(StaticURLTests.user)
        self.authorized_author.force_login(StaticURLTests.author)

    def test_post_url_request_status_for_guest(self):
        '''Проверка статусов страниц для гостевого пользователя'''
        url_names_status = {
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
            '/': HTTPStatus.OK,
            f'/group/{StaticURLTests.group.slug}/': HTTPStatus.OK,
            f'/profile/{StaticURLTests.author.username}/': HTTPStatus.OK,
            f'/posts/{StaticURLTests.post.id}/': HTTPStatus.OK,
            '/create/': HTTPStatus.FOUND,
            f'/posts/{StaticURLTests.post.id}/edit/': HTTPStatus.FOUND,
            f'/posts/{StaticURLTests.post.id}/comment/': HTTPStatus.FOUND,
        }
        for url, status in url_names_status.items():
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, status)

    def test_post_url_request_status_for_authorized(self):
        '''Проверка статусов страниц для авторизованного пользователя'''
        url_names_status = {
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
            '/': HTTPStatus.OK,
            f'/group/{StaticURLTests.group.slug}/': HTTPStatus.OK,
            f'/profile/{StaticURLTests.author.username}/': HTTPStatus.OK,
            f'/posts/{StaticURLTests.post.id}/': HTTPStatus.OK,
            '/create/': HTTPStatus.OK,
            f'/posts/{StaticURLTests.post.id}/edit/': HTTPStatus.FOUND,
            f'/posts/{StaticURLTests.post.id}/comment/': HTTPStatus.FOUND,
        }
        for url, status in url_names_status.items():
            with self.subTest(url=url):
                self.assertEqual(
                    self.authorized_client.get(url).status_code,
                    status
                )

    def test_post_url_request_status_for_author(self):
        '''Проверка статусов страниц для автора тестового поста'''
        url_names_status = {
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
            '/': HTTPStatus.OK,
            f'/group/{StaticURLTests.group.slug}/': HTTPStatus.OK,
            f'/profile/{StaticURLTests.author.username}/': HTTPStatus.OK,
            f'/posts/{StaticURLTests.post.id}/': HTTPStatus.OK,
            '/create/': HTTPStatus.OK,
            f'/posts/{StaticURLTests.post.id}/edit/': HTTPStatus.OK,
            f'/posts/{StaticURLTests.post.id}/comment/': HTTPStatus.FOUND,
        }
        for url, status in url_names_status.items():
            with self.subTest(url=url):
                self.assertEqual(
                    self.authorized_author.get(url).status_code,
                    status
                )

    def test_post_urls_uses_correct_template(self):
        '''URL-адрес использует соответствующий шаблон.'''
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{StaticURLTests.group.slug}/': 'posts/group_list.html',
            f'/profile/{StaticURLTests.author.username}/':
                'posts/profile.html',
            f'/posts/{StaticURLTests.post.id}/': 'posts/post_detail.html',
            f'/posts/{StaticURLTests.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                self.assertTemplateUsed(
                    self.authorized_author.get(address),
                    template
                )

    def test_private_pages_guests_redirection(self):
        '''Редирект гостей при попытке доступа к приватным страницам'''
        privite_urls = [
            reverse(
                'posts:post_edit',
                kwargs={'post_id': StaticURLTests.post.id}
            ),
            reverse('posts:post_create')
        ]
        for url in privite_urls:
            redirection_url = reverse('users:login') + '?next=' + url
            with self.subTest(url=url):
                self.assertRedirects(self.client.get(url), redirection_url)

    def test_post_edit_redirects_if_not_author(self):
        '''Редирект пользователя при попытке редактировать чужой пост'''
        testing_url = reverse(
            'posts:post_edit',
            kwargs={'post_id': StaticURLTests.post.id}
        )
        redirection_url = reverse(
            'posts:post_detail',
            kwargs={'post_id': StaticURLTests.post.id}
        )
        self.assertRedirects(
            self.authorized_client.get(testing_url),
            redirection_url
        )

    def test_post_comment_avalible_for_authorized(self):
        '''Только авторизованный пользователь может коментировать пост'''
        testing_url = f'/posts/{StaticURLTests.post.id}/comment/'
        redirection_success = f'/posts/{StaticURLTests.post.id}/'
        redirection_fail = f'/auth/login/?next={testing_url}'
        self.assertRedirects(
            self.authorized_client.get(testing_url),
            redirection_success
        )
        self.assertRedirects(
            self.client.get(testing_url),
            redirection_fail
        )

    def test_authorized_can_follow(self):
        '''Только авторизованный пользователь может подписаться/отписоваться'''
        testing_urls = [
            reverse(
                'posts:profile_follow',
                kwargs={'username': StaticURLTests.author.username}
            ),
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': StaticURLTests.author.username}
            ),
        ]
        redirection_success = reverse(
            'posts:profile',
            kwargs={'username': StaticURLTests.author.username}
        )
        for testing_url in testing_urls:
            with self.subTest(testing_url=testing_url):
                redirection_fail = (
                    reverse('users:login') + '?next=' + testing_url
                )
                self.assertRedirects(
                    self.client.get(testing_url),
                    redirection_fail
                )
                self.assertRedirects(
                    self.authorized_client.get(testing_url),
                    redirection_success
                )
