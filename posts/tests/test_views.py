from django import forms
import shutil
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model

from django.test import Client, TestCase
from django.urls import reverse
from django.conf import settings

from posts.models import User, Group, Post
from yatube.settings import POSTS_PER_PAGE

User = get_user_model()


class ViewModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.user = User.objects.create_user(username='test-user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(ViewModelTest.user)

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

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
            image=uploaded,
            author=ViewModelTest.user
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

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

    def check_image_in_page(self, response, objects):
        content = str(response.content)
        self.assertIn('<img class="card-img" src="/media/cache/', content)
        self.assertTrue(objects.image)

    def test_home_page_shows_correct_context(self):
        """Проверка главной страницы  на шаблон"""
        response = self.authorized_client.get(reverse('index'))
        post_object = response.context['page'][0]
        self.check_context_post(post_object)
        self.check_image_in_page(response, post_object)

    def test_group_page_shows_correct_context(self):
        """Проверка страницы группы на шаблон"""
        response = self.authorized_client.get(
            reverse('group_posts', args=[ViewModelTest.group.slug]))
        group_object = response.context['posts'][0]
        self.check_context_post(group_object)
        self.check_image_in_page(response, group_object)

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
        last_post = Post.objects.order_by('-pub_date')[0:1]
        self.assertEqual(ViewModelTest.posts, last_post.get())

    def test_index_create_new_post(self):
        """ Новый пост появляется на странице index """
        response = self.authorized_client.get(reverse('index'))
        post_object = response.context['page'][0]
        post_text_index = post_object
        last_post = Post.objects.order_by('-pub_date')[0:1]
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
                'post_edit',
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
            reverse('profile', kwargs={'username':
                                       ViewModelTest.posts.author.username}))
        post_object = response.context['page'][0]
        self.check_context_post(post_object)
        self.check_image_in_page(response, post_object)

    def test_post_user_post(self):
        """Проверка контекста страницы отдельног поста"""
        response = ViewModelTest.authorized_client.get(
            reverse(
                'post',
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
        self.check_image_in_page(response, post_object)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_group = (Group.objects.create(
            title='Группа для проверки пагинатора',
            slug='Test-slug-paginator',))
        cls.delta_posts = 3
        cls.array_posts = []
        for index_posts in range(
                POSTS_PER_PAGE + PaginatorViewsTest.delta_posts):
            username_par = f'Пользователь {index_posts}'
            PaginatorViewsTest.array_posts.append(Post.objects.create(
                text=f'Текст вашего поста{index_posts}',
                group=PaginatorViewsTest.test_group,
                author=User.objects.create(username=username_par)))

    def test_first_page_containse_ten_records(self):
        """Проверка правильной работы пагинатора 1ая страница"""
        response = self.client.get(reverse('index'))
        self.assertEqual(
            len(response.context.get('page').object_list), POSTS_PER_PAGE)

    def test_second_page_containse_three_records(self):
        """Проверка правильной работы пагинатора 2ая страница"""
        response = self.client.get(reverse('index'), {'page': 2})
        self.assertEqual(
            len(response.context.get('page').object_list),
            PaginatorViewsTest.delta_posts)
