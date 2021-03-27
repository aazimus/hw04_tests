# deals/tests/tests_models.py
from typing import Text
from django.forms import fields
from django.test import TestCase

from posts.models import Post, Group, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title='Название группы',
            slug='test-slug',
            description='Описание группы'
        )

        cls.posts = Post.objects.create(
            text='Текст вашего поста',
            group=cls.group,
            author=User.objects.create(username='artur')
        )

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.posts
        field_verboses = {
            'text': 'Текст вашего поста',
            'group': 'Группа'
        }

        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected
                )

    def test_help_text(self):
        """ help_text в полях совпадкет с ожиданием """
        post = PostModelTest.posts
        field_help_text = {
            'text': 'Текст вашего поста',
            'group': 'Группа'
        }

        for value, expected in field_help_text.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected
                )

    def test_str_post(self):
        post = PostModelTest.posts
        text = post.text
        self.assertEqual(str(post), text[0:15])

    def test_str_group(self):
        group = PostModelTest.group
        title = str(group)
        self.assertEqual(title, group.title)
