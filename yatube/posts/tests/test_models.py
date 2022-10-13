from django.contrib.auth import get_user_model
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
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
            name='small.gif', content=cls.small_gif, content_type='image/gif')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            image=cls.uploaded
        )

    def test_models_have_correct_group_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        field_verboses = {
            PostModelTest.group.title: 'Тестовая группа',
            PostModelTest.group.slug: 'Тестовый слаг',
            PostModelTest.group.description: 'Тестовое описание',
            PostModelTest.post.text: 'Тестовый пост',
        }

        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected_value)

    def test_title_label(self):
        """verbose_name поля  совпадает с ожидаемым."""
        task = PostModelTest.post
        field_verboses = {
            'text': 'текст',
            'pub_date': 'дата публикации',
            'author': 'автор',
            'group': 'Группа',
            'image': 'Картинка',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                verbose = task._meta.get_field(field).verbose_name
                self.assertEqual(verbose, expected_value)

    def test_title_help_text(self):
        """help_text поля совпадает с ожидаемым."""
        task = PostModelTest.post
        field_verboses = {
            'text': 'Здесь должен быть текст',
            'group': 'Здесь группа'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                verbose = task._meta.get_field(field).help_text
                self.assertEqual(verbose, expected_value)
