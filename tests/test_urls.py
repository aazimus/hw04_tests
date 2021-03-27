from django.http import response
from posts.views import index
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Group, User,Post

class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        response = self.guest_client.get(reverse('index'))  
        self.assertEqual(response.status_code, 200) 


class Test_Client_Url(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='author_post')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user) 

        cls.user_non_author_post = User.objects.create_user(username='Non_author_post')
        cls.authorized_non_author_post = Client()
        cls.authorized_non_author_post.force_login(cls.user_non_author_post)
        
        cls.guest_client = Client()

        super().setUpClass()
        cls.group = Group.objects.create(
            title = 'Группа1',
            slug = 'teg',
            description = 'Teg'
        )

        cls.posts = Post.objects.create(
            text='Текст вашего поста',
            group = cls.group,
            author = Test_Client_Url.user
        )

        # Первый в списке код - проверка не авторизированного пользователя,второй в списке код проверка авторизированного пользователя
        cls.urls_code = {            
        reverse('index',args = None):[200,200],
        reverse('new_post',args = None):[302,200],
        reverse("group_posts",args = [Test_Client_Url.group.slug]):[200,200],
        reverse("profile" ,args = [Test_Client_Url.posts.author.username]):[200,200],
        reverse("post", kwargs = {'username':Test_Client_Url.posts.author.username,'post_id':Test_Client_Url.posts.id}):[200,200],
        reverse("post_edit",kwargs = {'username':Test_Client_Url.posts.author.username,'post_id':Test_Client_Url.posts.id}):[302,200],
        reverse('about:author'):[200,200],
        reverse('about:tech'):[200,200],
        
        }
                

    def test_home_url_exists_at_desired_location(self):
        """Тесты на не авторизированного пользователя прошли"""                
        for urls,none_user_code in Test_Client_Url.urls_code.items():
            with self.subTest():
                response = self.guest_client.get(urls)
                print('Проверка',urls)
                self.assertEqual(response.status_code,none_user_code[0])           
    
    def test_home_url_user_location(self):
        """Тесты на авторизированного пользователя прошли"""
        for urls, authorized_user_code in Test_Client_Url.urls_code.items():
            with self.subTest():
                response = self.authorized_client.get(urls)
                print('Проверка',urls)                
                self.assertEqual(response.status_code,authorized_user_code[1])

    def test_post_edit_url_author_posts(self):
        """Проверка доступа к редактированию поста не автора поста"""
        response = self.authorized_non_author_post.get(
            reverse("post_edit",kwargs ={
            'username':Test_Client_Url.posts.author.username,
            'post_id':Test_Client_Url.posts.id})            
            )
        self.assertEqual(response.status_code,302)          

    def test_urls_uses_correct_template(self):
        """ URL-адрес использует соответствующий шаблон. """
        templates_url_names = {
        'index.html': reverse('index'),
        'new.html': reverse('new_post'),
        'group.html': reverse('group_posts',args= [Test_Client_Url.group.slug]),
        'new.html':reverse("post_edit",kwargs ={'username':Test_Client_Url.posts.author.username,'post_id':Test_Client_Url.posts.id}),
        'about/author.html':reverse('about:author'),
        'about/tech.html':reverse('about:tech'),
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                print("Проверка",reverse_name)
                self.assertTemplateUsed(response, template) 

    def test_new_url_redirect_anonymous_on_admin_login(self):
        """ Перенаправление не авторизированиго пользователя с new на регистрацию"""
        response = Test_Client_Url.guest_client.get(reverse('new_post'), follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/new/')  
                                     