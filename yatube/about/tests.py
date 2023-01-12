from django.test import TestCase, Client


class StaticURLTests(TestCase):
    '''Класс тестов доступности url адресов'''
    def setUp(self):
        '''Фикстуры класса'''
        self.guest_client = Client()

    def test_about_urls_uses_correct_templates(self):
        '''В приложении about используются кореектные шаблоны страниц'''
        templates_url_names = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
