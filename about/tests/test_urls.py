from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from posts.models import User


class TestClientUrl(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='author_post')
        super().setUpClass()
        cls.urls_code = {
            '/about/author/':
            {'unauth': HTTPStatus.OK, 'auth': HTTPStatus.OK, },
            '/about/tech/':
            {'unauth': HTTPStatus.OK, 'auth': HTTPStatus.OK, },
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(TestClientUrl.user)

    def test_home_url_exists_at_desired_location_about(self):
        """Тесты на не авторизированного пользователя прошли"""
        for urls, none_user_code in TestClientUrl.urls_code.items():
            with self.subTest():
                response = self.guest_client.get(urls)
                self.assertEqual(
                    response.status_code,
                    none_user_code['unauth'])

    def test_home_url_user_location(self):
        """Тесты на авторизированного пользователя прошли"""
        for urls, authorized_user_code in TestClientUrl.urls_code.items():
            with self.subTest():
                response = self.authorized_client.get(urls)
                self.assertEqual(
                    response.status_code, authorized_user_code['auth'])

    def test_urls_uses_correct_template(self):
        """ URL-адрес использует соответствующий шаблон. """
        templates_url_names = {
            'author.html': reverse('about:author'),
            'tech.html': reverse('about:tech'),
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
