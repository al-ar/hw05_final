from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Post, Group
from http import HTTPStatus
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Grouppa',
            slug='test-slug',
            description='описание'
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif', content=cls.small_gif, content_type='image/gif'
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {'text': 'Написали новый пост',
                     'group': self.group.id, 'image': self.uploaded}
        response = self.authorized_client.post(
            reverse('posts:create_post'), data=form_data, follow=True
        )
        self.assertRedirects(response, reverse('posts:profile',
                             kwargs={'username': self.user.username}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.filter(
                        text='Написали новый пост').exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)
        post = Post.objects.get(text='Написали новый пост')
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, self.group)
        self.assertTrue(post.image)

    def test_post_edit(self):
        """Валидная форма изменяет запись в Post."""
        self.post = Post.objects.create(
            author=self.user,
            text='Написали новый пост',
        )
        self.new_group = Group.objects.create(
            title='Groupp',
            slug='test2-slug',
            description='Тестовое описание 2',
        )
        posts_count = Post.objects.count()

        form_data = {
            'text': 'Изменили текст поста',
            'group': self.new_group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=({self.post.id})),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(Post.objects.filter(
                        text='Изменили текст поста').exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotIn(Post.objects.filter(
                         text='Изменили текст поста'),
                         Post.objects.filter(group=self.group))

    def test_post_edit_not_create_guest_client(self):
        """Валидная форма не изменит запись в Post если неавторизован."""
        self.post = Post.objects.create(
            author=self.user,
            text='Написали новый пост',
        )
        posts_count = Post.objects.count()
        form_data = {'text': 'Изменили текст поста', 'group': self.group.id}
        response = self.guest_client.post(
            reverse('posts:post_edit', args=({self.post.id})),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response,
                             f'/auth/login/?next=/posts/{self.post.id}/edit/')
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFalse(Post.objects.filter(
                         text='Изменили текст поста').exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)
