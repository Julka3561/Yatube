from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()

GROUP_TITLE = 'Тестовая группа'
GROUP_SLUG = 'test-slug'
GROUP_DESCRIPTION = 'Тестовое описание'
GROUP_ID = 1
AUTHOR = 'author'
USER = 'test-user'
POST_ID = 1
POST_TEXT = 'Тестовый пост'

URL_NAMES_TEMPLATES_WITHOUT_AUTH = {
    reverse('posts:index'): 'posts/index.html',
    reverse('posts:group_list', kwargs={'group_list': GROUP_SLUG}):
        'posts/group_list.html',
    reverse('posts:profile', kwargs={'username': USER}):
        'posts/profile.html',
    reverse('posts:post_detail', kwargs={'pk': POST_ID}):
        'posts/post_detail.html',
}

URL_NAMES_TEMPLATES_WITH_AUTH = {
    reverse('posts:post_edit', kwargs={'pk': POST_ID}):
        'posts/create_post.html',
    reverse('posts:post_create'): 'posts/create_post.html',
    reverse('posts:follow_index'): 'posts/follow.html',
}

URL_NAMES_TEMPLATES_ALL = {
    **URL_NAMES_TEMPLATES_WITHOUT_AUTH,
    **URL_NAMES_TEMPLATES_WITH_AUTH
}

URL_NAMES_WITH_AUTH = [
    reverse('posts:add_comment', kwargs={'pk': POST_ID}),
    reverse('posts:profile_follow', kwargs={'username': AUTHOR}),
    reverse('posts:profile_unfollow', kwargs={'username': AUTHOR}),
]


class PostsURLTests(TestCase):
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
        )

    def setUp(self):
        # неавторизованный пользователь
        self.guest_client = Client()
        # авторизованный пользователь
        self.user = User.objects.create_user(username=USER)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # авторизованный пользователь, автор поста
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.author)

    def test_for_without_auth_urls_exists_at_desired_location(self):
        """Проверка доступности адресов не требующих аутентификации posts"""
        for address in URL_NAMES_TEMPLATES_WITHOUT_AUTH:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_for_with_auth_urls_exists_at_desired_location(self):
        """Проверка доступности адресов требующих аутентификации posts"""
        for address in URL_NAMES_TEMPLATES_WITH_AUTH:
            with self.subTest(address=address):
                response = self.authorized_client_author.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirects_for_unautorized_users(self):
        """Проверка редиректов на страницу аутентификации posts"""
        for address in URL_NAMES_TEMPLATES_WITH_AUTH:
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(response, f'/auth/login/?next={address}')

    def test_redirect_for_edit_post(self):
        """Проверка редиректа на страницу поста, если пользователь не автор"""
        response = self.authorized_client.get('/posts/1/edit/', follow=True)
        self.assertRedirects(response, '/posts/1/')

    def test_url_uses_correct_template(self):
        """Проверка шаблонов страниц приложения posts"""
        for address, template in URL_NAMES_TEMPLATES_ALL.items():
            with self.subTest(address=address):
                response = self.authorized_client_author.get(address)
                self.assertTemplateUsed(response, template)

    def test_unexisting_page_error_404(self):
        """Проверка вывода ошибки 404 при несуществующем адресе"""
        response = self.authorized_client_author.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_redirects_for_comment_and_follow(self):
        """Проверка редиректа при комментировании и подписке/отписке"""
        for address in URL_NAMES_WITH_AUTH:
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(response, f'/auth/login/?next={address}')
