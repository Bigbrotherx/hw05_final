from http import HTTPStatus

from django.test import TestCase


class ViewTests(TestCase):
    '''Класс тестов приложения Core'''
    def test_core_404_page_uses_custom_template(self):
        '''Для страницы ошибки 404 используется касстомный шаблон'''
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
