from core.models import CreatedModel
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

QTY_OF_SYMBOLS = 15


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=80, unique=True)
    description = models.TextField()

    class Meta:
        verbose_name = 'группа'
        verbose_name_plural = 'группы'

    def __str__(self):
        return self.title


class Post(CreatedModel):
    text = models.TextField(help_text='Введите текст поста',
                            verbose_name='Текст поста')
    group = models.ForeignKey(
        Group,
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        help_text='Выберите группу',
        verbose_name='Группа',
    )
    image = models.ImageField(
        verbose_name='Картинка',
        help_text='Загрузите картинку',
        upload_to='posts/',
        blank=True,
    )

    class Meta:
        ordering = ['-created']
        verbose_name = 'пост'
        verbose_name_plural = 'посты'

    def __str__(self):
        return self.text[:QTY_OF_SYMBOLS]


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост',
    )
    text = models.TextField(help_text='Напишите свой комментарий',
                            verbose_name='Комментарий',
                            max_length=150)

    class Meta:
        ordering = ['-created']
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'

    def __str__(self):
        return self.text[:QTY_OF_SYMBOLS]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )
