from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

GROUP_TITLE = 'Тестовая группа'
GROUP_SLUG = 'test-slug'
GROUP_DESCRIPTION = 'Тестовое описание'
GROUP_ID = 1
AUTHOR = 'author'
POST_TEXT = 'Тестовый пост'

User = get_user_model()


class IndexCacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=AUTHOR)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text=POST_TEXT,
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.author)

    def test_index_page_is_cached(self):
        """Проверки работы кэширования главной страницы сайта"""
        response = self.authorized_client_author.get(reverse('posts:index'))
        content1 = response.content
        post = response.context['page_obj'][0]
        post_text = post.text
        post_author = post.author.username
        post_group_slug = post.group.slug
        self.assertEqual(post_text, POST_TEXT)
        self.assertEqual(post_author, AUTHOR)
        self.assertEqual(post_group_slug, GROUP_SLUG)
        self.post.delete()
        response = self.authorized_client_author.get(reverse('posts:index'))
        content2 = response.content
        self.assertEqual(content1, content2)
        cache.clear()
        response = self.authorized_client_author.get(reverse('posts:index'))
        content3 = response.content
        self.assertNotEqual(content1, content3)
