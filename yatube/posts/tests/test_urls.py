from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from ..models import Group, Post
from http import HTTPStatus


User = get_user_model()


class StaticURLTests(TestCase):
    """"Статические страницы  доступны любому пользователю."""
    def test_aboutpage(self):
        self.guest_client = Client()
        url_names = {
            '/about/tech/': HTTPStatus.OK,
            '/about/author/': HTTPStatus.OK
        }
        for address, code in url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, code)


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='AuthorName')
        cls.group = Group.objects.create(
            title='Grouppa',
            slug='test-slug',
            description='описание'
        )
        cls.post = Post.objects.create(
            text='Текст нового поста',
            author=cls.user_author,
            id=88,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.post.author)

    def test_url_guest_client(self):
        """Страницы доступны любому пользователю."""
        url_name = {
            '/': HTTPStatus.OK,
            '/group/test-slug/': HTTPStatus.OK,
            f'/profile/{self.user}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/edit/': HTTPStatus.FOUND,
            '/create/': HTTPStatus.FOUND,
            '/unexisting/': HTTPStatus.NOT_FOUND,
        }
        for address, code in url_name.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, code)

    def test_url_authorized_client(self):
        """Страницы доступнаы авторизованному пользователю."""
        url_name = {
            '/': HTTPStatus.OK,
            '/group/test-slug/': HTTPStatus.OK,
            f'/profile/{self.user}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/edit/': HTTPStatus.FOUND,
            '/create/': HTTPStatus.OK,
            '/unexisting/': HTTPStatus.NOT_FOUND,
        }
        for address, code in url_name.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, code)

    def test_url_author_client(self):
        """Страница редактирования доступна автору поста."""
        response = self.authorized_author.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """проверяем соответствие шаблонов"""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/HasNoName/': 'posts/profile.html',
            '/posts/88/': 'posts/post_detail.html',
            '/posts/88/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_author.get(address)
                self.assertTemplateUsed(response, template)
