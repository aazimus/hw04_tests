from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Group, User, Post


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        response = self.guest_client.get(reverse('index'))
        self.assertEqual(response.status_code, HTTPStatus.OK)


class TestClientUrl(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='author_post')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.user_non_author_post = User.objects.create_user(
            username='Non_author_post')
        cls.authorized_non_author_post = Client()
        cls.authorized_non_author_post.force_login(cls.user_non_author_post)

        cls.guest_client = Client()

        super().setUpClass()
        cls.group = Group.objects.create(
            title='Группа1',
            slug='teg',
            description='Teg'
        )

        cls.posts = Post.objects.create(
            text='Текст вашего поста',
            group=cls.group,
            author=TestClientUrl.user
        )

        cls.urls_code = {
            reverse('index', args=None): {'unauth': HTTPStatus.OK, 'auth': HTTPStatus.OK, },
            reverse('new_post', args=None): {'unauth': HTTPStatus.FOUND, 'auth': HTTPStatus.OK, },
            reverse('group_posts',
                    args=[TestClientUrl.group.slug]):
            {'unauth': HTTPStatus.OK, 'auth': HTTPStatus.OK, },
            reverse('profile',
                    args=[TestClientUrl.posts.author.username]):
            {'unauth': HTTPStatus.OK, 'auth': HTTPStatus.OK, },
            reverse('post', kwargs={'username':
                                    TestClientUrl.posts.author.username,
                                    'post_id': TestClientUrl.posts.id}):
            {'unauth': HTTPStatus.OK, 'auth': HTTPStatus.OK, },
            reverse('post_edit',
                    kwargs={'username': TestClientUrl.posts.author.username,
                            'post_id': TestClientUrl.posts.id}):
            {'unauth': HTTPStatus.FOUND, 'auth': HTTPStatus.OK, },
            reverse('about:author'): {'unauth': HTTPStatus.OK, 'auth': HTTPStatus.OK, },
            reverse('about:tech'): {'unauth': HTTPStatus.OK, 'auth': HTTPStatus.OK, },

        }

    def test_home_url_exists_at_desired_location(self):
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

    def test_post_edit_url_author_posts(self):
        """Проверка доступа к редактированию поста не автора поста"""
        response = self.authorized_non_author_post.get(
            reverse('post_edit', kwargs={
                'username': TestClientUrl.posts.author.username,
                'post_id': TestClientUrl.posts.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_uses_correct_template(self):
        """ URL-адрес использует соответствующий шаблон. """
        templates_url_names = {
            'index.html': reverse('index'),
            'posts/new.html': reverse('new_post'),
            'group.html': reverse('group_posts',
                                  args=[TestClientUrl.group.slug]),
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_urls_new_corret_templates(self):
        template = 'posts/new.html'
        response = self.authorized_client.get(
            reverse('post_edit',
                    kwargs={
                        'username':
                        TestClientUrl.posts.author.username,
                        'post_id':
                        TestClientUrl.posts.id}),)
        self.assertTemplateUsed(response, template)

    def test_new_url_redirect_anonymous_on_admin_login(self):
        """ Редирект не авторизированиго пользователя с new на регистрацию"""
        response = TestClientUrl.guest_client.get(
            reverse('new_post'), follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/new/')
