from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import User, Group, Post

User = get_user_model()


class ViewModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test-user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(ViewModelTest.user)

        cls.group2 = Group.objects.create(
            title='Название группы 2',
            slug='test2-slug',
            description='Test-slug'
        )

        cls.group = Group.objects.create(
            title='Название группы',
            slug='test-slug',
            description='Test-slug'
        )

        cls.posts = Post.objects.create(
            text='Текст вашего поста',
            group=cls.group,
            author=ViewModelTest.user
        )

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'index.html': reverse('index'),
            'new.html': reverse('new_post'),
            'group.html': reverse('group_posts',
                                  args=[ViewModelTest.group.slug])
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def check_context_post(self, objects):
        self.assertEqual(objects.pub_date, ViewModelTest.posts.pub_date)
        self.assertEqual(objects.text, ViewModelTest.posts.text)
        self.assertEqual(objects.author.username,
                         ViewModelTest.posts.author.username)

    def test_home_page_shows_correct_context(self):
        """Проверка главной страницы  на шаблон"""
        response = self.authorized_client.get(reverse('index'))
        post_object = response.context['page'][0]
        self.check_context_post(post_object)

    def test_group_page_shows_correct_context(self):
        """Проверка страницы группы на шаблон"""
        response = self.authorized_client.get(
            reverse('group_posts', args=[ViewModelTest.group.slug]))
        group_object = response.context['posts'][0]
        self.check_context_post(group_object)

    def test_new_posts_page_shows_correct_context(self):
        """Проверка страницы нового поста  на шаблон"""
        response = self.authorized_client.get(reverse('new_post'))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_create_new_post(self):
        """ Посты совападют """
        last_post = Post.objects.order_by("-pub_date")[0:1]
        self.assertEqual(ViewModelTest.posts, last_post.get())

    def test_index_create_new_post(self):
        """ Новый пост появляется на странице index """
        response = self.authorized_client.get(reverse('index'))
        post_object = response.context['page'][0]
        post_text_index = post_object
        last_post = Post.objects.order_by("-pub_date")[0:1]
        self.assertEqual(post_text_index, last_post.get())

    def test_new_post_group_identification(self):
        """ Новый пост  не  появляетя не в своей группе """
        response = self.authorized_client.get(
            reverse('group_posts', args=[ViewModelTest.group2.slug]))
        post_count = len(response.context['posts'])
        self.assertEqual(post_count, 0)

    def test_post_edit_correct_context(self):
        """Проверка страницы редактирования поста  на шаблон"""
        response = ViewModelTest.authorized_client.get(
            reverse(
                "post_edit",
                kwargs={
                    'username': self.posts.author.username,
                    'post_id': self.posts.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_profile_user_post(self):
        """Проверка контекста страницы профайла на контекст"""
        response = ViewModelTest.authorized_client.get(
            reverse("profile", kwargs={'username':
                                       ViewModelTest.posts.author.username}))
        post_object = response.context['page'][0]
        self.check_context_post(post_object)

    def test_post_user_post(self):
        """Проверка контекста страницы отдельног поста"""
        response = ViewModelTest.authorized_client.get(
            reverse(
                "post",
                kwargs={
                    'username': ViewModelTest.posts.author.username,
                    'post_id': ViewModelTest.posts.id}))
        post_object = response.context['post']
        post_text = post_object.text
        count_object = response.context['post_count']
        user_object = response.context['user']

        self.assertEqual(post_text, ViewModelTest.posts.text)
        self.assertEqual(
            count_object, Post.objects.filter(
                author=ViewModelTest.posts.author).count())
        self.assertEqual(user_object, ViewModelTest.user)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_group = (Group.objects.create(
            title='Группа для проверки пагинатора',
            slug='Test-slug-paginator',))

        cls.array_posts = []
        for index_posts in range(13):
            username_par = f'Пользователь {index_posts}'
            PaginatorViewsTest.array_posts.append(Post.objects.create(
                text=f'Текст вашего поста{index_posts}',
                group=PaginatorViewsTest.test_group,
                author=User.objects.create(username=username_par)))

    def test_first_page_containse_ten_records(self):
        """Проверка правильной работы пагинатора 1ая страница"""
        response = self.client.get(reverse('index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_containse_three_records(self):
        """Проверка правильной работы пагинатора 2ая страница"""
        response = self.client.get(reverse('index'), {'page': 2})
        self.assertEqual(len(response.context.get('page').object_list), 3)
