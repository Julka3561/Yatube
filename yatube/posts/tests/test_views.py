import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post

# создаем временную папку для медиа-файлов
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()

# тестовые данные для всех классов тестов
GROUP_TITLE = 'Тестовая группа'
GROUP_SLUG = 'test-slug'
GROUP_DESCRIPTION = 'Тестовое описание'
GROUP_ID = 1
AUTHOR = 'author'
POST_TEXT = 'Тестовый пост'


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    # тестовые данные
    GROUP_TITLE_2 = 'Другая группа'
    GROUP_SLUG_2 = 'another_group'
    GROUP_DESCRIPTION_2 = 'Группа для проверки, что пост попал только в нужную'
    POST_ID = 1
    NUMBER_OF_POSTS = 1
    SMALL_GIF = (
        b'\x47\x49\x46\x38\x39\x61\x01\x00'
        b'\x01\x00\x00\x00\x00\x21\xf9\x04'
        b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
        b'\x00\x00\x01\x00\x01\x00\x00\x02'
        b'\x02\x4c\x01\x00\x3b'
    )
    POST_IMAGE = SimpleUploadedFile(
        name='small.gif',
        content=SMALL_GIF,
        content_type='image/gif',
    )
    COMMENT_TEXT = 'Тестовый комментарий'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=AUTHOR)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.another_group = Group.objects.create(
            title=cls.GROUP_TITLE_2,
            slug=cls.GROUP_SLUG_2,
            description=cls.GROUP_DESCRIPTION_2,
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text=POST_TEXT,
            group=cls.group,
            image=cls.POST_IMAGE
        )
        cls.comment = Comment.objects.create(
            text=cls.COMMENT_TEXT,
            author=cls.author,
            post=cls.post,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # удаление временной папки после тестов
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # неавторизованный пользователь
        self.guest_client = Client()
        # авторизованный пользователь, автор поста
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.author)

    def test_pages_uses_correct_template(self):
        """Адрес вида namespace:name использует соответствующий шаблон"""
        page_names_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'group_list': GROUP_SLUG}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': AUTHOR}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'pk': self.POST_ID}):
                'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'pk': self.POST_ID}):
                'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in page_names_templates.items():
            with self.subTest(template=template):
                response = self.authorized_client_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def post_check(self, post):
        """Метод для проверки правильности содержимого поста"""
        post_text = post.text
        post_author = post.author.username
        post_group_slug = post.group.slug
        post_image = post.image
        self.assertEqual(post_text, POST_TEXT)
        self.assertEqual(post_author, AUTHOR)
        self.assertEqual(post_group_slug, GROUP_SLUG)
        self.assertEqual(post_image, f'posts/{self.POST_IMAGE.name}')

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом"""
        response = self.guest_client.get(reverse('posts:index'))

        first_post = response.context['page_obj'][0]
        self.post_check(first_post)

        page_title = response.context['title']
        self.assertEqual(page_title, 'Это главная страница проекта Yatube')

    def test_group_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом"""
        response = self.guest_client.get(reverse(
            'posts:group_list', kwargs={'group_list': GROUP_SLUG}))

        first_post = response.context['page_obj'][0]
        self.post_check(first_post)
        self.assertNotEqual(first_post.group.slug, self.GROUP_SLUG_2)

        group_obj = response.context['group']
        group_title = group_obj.title
        group_desciption = group_obj.description
        self.assertEqual(group_title, GROUP_TITLE)
        self.assertEqual(group_desciption, GROUP_DESCRIPTION)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом"""
        response = self.guest_client.get(reverse(
            'posts:profile', kwargs={'username': AUTHOR}))

        first_post = response.context['page_obj'][0]
        self.post_check(first_post)

        author_obj = response.context['author']
        author_username = author_obj.username
        self.assertEqual(author_username, AUTHOR)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом"""
        response = self.guest_client.get(reverse(
            'posts:post_detail', kwargs={'pk': self.POST_ID}))

        detailed_post = response.context['post']
        self.post_check(detailed_post)

        number_of_posts = response.context['post_count']
        self.assertEqual(number_of_posts, self.NUMBER_OF_POSTS)

        form_field_expected = forms.fields.CharField
        form_field = response.context['form'].fields['text']
        self.assertIsInstance(form_field, form_field_expected)
        # проверка начальных значений формы
        self.assertIsNone(form_field.initial)

        first_comment = response.context['comments'][0]
        self.assertEqual(first_comment.text, self.COMMENT_TEXT)
        self.assertEqual(first_comment.author.username, AUTHOR)
        self.assertEqual(first_comment.post.id, self.POST_ID)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом"""
        response = self.authorized_client_author.get(reverse(
            'posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
                # проверка начальных значений формы
                self.assertIsNone(form_field.initial)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом"""
        response = self.authorized_client_author.get(reverse(
            'posts:post_edit', kwargs={'pk': self.POST_ID}))
        form_fields = {
            'text': [forms.fields.CharField, POST_TEXT],
            'group': [forms.fields.ChoiceField, GROUP_ID],
            'image': [forms.fields.ImageField, f'posts/{self.POST_IMAGE.name}']
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected[0])
                # проверка заполнения формы данными из поста
                form_field_value = response.context['form'][value].value()
                self.assertEqual(form_field_value, expected[1])

        post_id = response.context['post_id']
        self.assertEqual(post_id, self.POST_ID)

        is_edit = response.context['is_edit']
        self.assertTrue(is_edit)


class PaginatorViewsTest(TestCase):
    # тестовые данные
    PAGES_WITH_PAGINATOR = [
        reverse('posts:index'),
        reverse('posts:group_list', kwargs={'group_list': GROUP_SLUG}),
        reverse('posts:profile', kwargs={'username': AUTHOR}),
    ]
    QTY_OF_POSTS = 13
    QTY_OF_POSTS_ON_PAGE = [10, 3]
    NUMBER_OF_PAGES = 2

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=AUTHOR)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        for i in range(cls.QTY_OF_POSTS):
            cls.post = Post.objects.create(
                author=cls.author,
                text=POST_TEXT,
                group=cls.group,
            )

    def setUp(self):
        # неавторизованный пользователь
        self.guest_client = Client()

    def test_pages_contain_right_amount_of_records(self):
        """Проверка работы пагинатора: количество постов на странице"""
        for address in self.PAGES_WITH_PAGINATOR:
            for page in range(self.NUMBER_OF_PAGES):
                with self.subTest(address=address):
                    response = self.guest_client.get(address
                                                     + f'?page={page+1}')
                    self.assertEqual(len(response.context['page_obj']),
                                     self.QTY_OF_POSTS_ON_PAGE[page])

    def test_pages_show_correct_context(self):
        """Проверка работы пагинатора: содержимое контекста"""
        for address in self.PAGES_WITH_PAGINATOR:
            for page in range(self.NUMBER_OF_PAGES):
                with self.subTest(address=address):
                    response = self.guest_client.get(address
                                                     + f'?page={page+1}')
                    post_list = response.context.get('page_obj').object_list
                    first_post = post_list[0]
                    post_text = first_post.text
                    post_author = first_post.author.username
                    post_group_slug = first_post.group.slug
                    self.assertEqual(post_text, POST_TEXT)
                    self.assertEqual(post_author, AUTHOR)
                    self.assertEqual(post_group_slug, GROUP_SLUG)


class FollowViewsTest(TestCase):
    USER = 'test-user'
    USER2 = 'test-user-not-follower'
    NO_POSTS_ON_PAGE = 0

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
        # авторизованный пользователь
        self.user = User.objects.create_user(username=self.USER)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.user2 = User.objects.create_user(username=self.USER2)
        self.not_follower_client = Client()
        self.not_follower_client.force_login(self.user)

    def test_user_can_follow_and_unfollow_author(self):
        """Зарегистрированный пользователь может подписываться на автора
         и отписываться от него
        """
        # подписка на автора
        self.authorized_client.get(reverse(
            'posts:profile_follow', kwargs={'username': AUTHOR}))
        # проверка содержимого страницы follow
        response = self.authorized_client.get(reverse('posts:follow_index'))
        posts = response.context.get('page_obj').object_list
        first_post = posts[0]
        post_text = first_post.text
        post_author = first_post.author.username
        post_group_slug = first_post.group.slug
        self.assertEqual(post_text, POST_TEXT)
        self.assertEqual(post_author, AUTHOR)
        self.assertEqual(post_group_slug, GROUP_SLUG)
        # отписка от автора
        self.authorized_client.get(reverse(
            'posts:profile_unfollow', kwargs={'username': AUTHOR}))
        # проверка содержимого страницы follow
        response = self.authorized_client.get(reverse('posts:follow_index'))
        posts_count = response.context.get('page_obj').object_list.count()
        self.assertEqual(posts_count, self.NO_POSTS_ON_PAGE)

    def test_new_post_only_for_follower(self):
        """Новый пост появляется только в ленте фолловеров"""
        response = self.not_follower_client.get(reverse('posts:follow_index'))
        posts_count = response.context.get('page_obj').object_list.count()
        self.assertEqual(posts_count, self.NO_POSTS_ON_PAGE)
