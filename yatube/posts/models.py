
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
LIMIT_TEXT: int = 15


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='титл')
    slug = models.SlugField(unique=True, verbose_name='адрес')
    description = models.TextField(verbose_name='описание')

    def __str__(self):
        return self.title[:LIMIT_TEXT]


class Post(models.Model):
    text = models.TextField(verbose_name='текст',
                            help_text='Здесь должен быть текст')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='дата публикации')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='автор',
    )
    group = models.ForeignKey(
        Group, blank=True, null=True,
        on_delete=models.SET_NULL, related_name='posts', verbose_name='Группа',
        help_text='Здесь группа'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self):
        return self.text[:LIMIT_TEXT]

    class Meta:
        ordering = ['-pub_date']


class Comments (models.Model):
    post = models.ForeignKey(
        Post, null=True, blank=True,
        on_delete=models.CASCADE, related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True,)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.text


class Follow (models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )

    def __str__(self):
        return self.text
