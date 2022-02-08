from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import QTY_OF_SYMBOLS, Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    # тестовые данные
    GROUP_TITLE = 'Тестовая группа'
    GROUP_SLUG = 'test-slug'
    GROUP_DESCRIPTION = 'Тестовое описание'
    AUTHOR = 'author'
    POST_TEXT = 'Тестовый пост'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=cls.AUTHOR)
        cls.group = Group.objects.create(
            title=cls.GROUP_TITLE,
            slug=cls.GROUP_SLUG,
            description=cls.GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=cls.POST_TEXT,
        )

    def test_models_have_correct_object_names(self):
        """Объекты моделей Group и Post правильно выводятся в __str__"""
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

        post = PostModelTest.post
        expected_object_name = post.text[:QTY_OF_SYMBOLS]
        self.assertEqual(expected_object_name, str(post))

    def test_verbose_name(self):
        """verbose_name в полях модели Post совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'created': 'Дата создания',
            'author': 'Автор',
            'group': 'Группа',
            'image': 'Картинка',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_help_text(self):
        """help_text в полях модели Post совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу',
            'image': 'Загрузите картинку',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)
