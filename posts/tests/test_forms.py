from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group, User


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test-user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.guest_client = Client()

        cls.group = Group.objects.create(
            title='Название группы',
            slug='test-slug',
            description='Описание группы'
        )
        cls.post = Post.objects.create(
            text='Текст вашего поста',
            group=cls.group,
            author=PostCreateFormTests.user
        )

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'text',
            'group': PostCreateFormTests.group.id,
            'author': self.user
        }

        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=False
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='text',
                group=PostCreateFormTests.group.id
            ).exists()
        )

    def test_post_edit_change_post(self):
        """Проверка на изменинеие поста через post_edit  """
        post_count = Post.objects.count()
        fix_form_data = {
            'text': 'Отредактрированный текст',
            'group': PostCreateFormTests.group.id
        }
        response = self.authorized_client.post(
            reverse('post_edit',
                    kwargs={'username': PostCreateFormTests.user.username,
                            'post_id': PostCreateFormTests.post.id}),
            data=fix_form_data, follow=False)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Post.objects.count(), post_count)
        self.assertTrue(
            Post.objects.filter(
                text='Отредактрированный текст',
                group=PostCreateFormTests.group.id
            ).exists()
        )

    def test_guest_client_post_edit_change(self):
        """Проверка Не авторизированый пользователь"""
        """не может редактировать пост  """
        post_count = Post.objects.count()
        fix_form_data = {
            'text': 'Отредактрированный текст',
            'group': PostCreateFormTests.group.id
        }
        response = self.guest_client.post(
            reverse('post_edit',
                    kwargs={'username': PostCreateFormTests.user.username,
                            'post_id': PostCreateFormTests.post.id}),
            data=fix_form_data, follow=False)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Post.objects.count(), post_count)
        self.assertFalse(
            Post.objects.filter(
                text='Отредактрированный текст',
                group=PostCreateFormTests.group.id
            ).exists()
        )

    def test_guest_client_create_post(self):
        """Не авторизированый пользователь не может создавать новый пост."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'text',
            'group': PostCreateFormTests.group.id,
            'author': self.user
        }
        # Отправляем POST-запрос
        response = self.guest_client.post(
            reverse('new_post'),
            data=form_data,
            follow=False
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Post.objects.count(), post_count)
        self.assertFalse(
            Post.objects.filter(
                text='text',
                group=PostCreateFormTests.group.id
            ).exists()
        )
