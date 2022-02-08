import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Comment, Group, Post

# создаем временную папку для медиа-файлов
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateAndEditFormTests(TestCase):
    # тестовые данные
    GROUP_TITLE = 'Тестовая группа'
    GROUP_SLUG = 'test-slug'
    GROUP_DESCRIPTION = 'Тестовое описание'
    GROUP_ID = 1
    GROUP_ID_EDITED = ''
    AUTHOR = 'author'
    USER = 'test-user'
    POST_TEXT = 'Тестовый пост'
    POST_TEXT_EDITED = 'Тестовый пост. Редактирование'
    POST_ID = 1
    NEW_POST_ID = 2
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
    POST_IMAGE_EDITED = SimpleUploadedFile(
        name='small2.gif',
        content=SMALL_GIF,
        content_type='image/gif',
    )
    POST_COMMENT = 'Тестовый комментарий'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=cls.AUTHOR)
        cls.group = Group.objects.create(
            title=cls.GROUP_TITLE,
            slug=cls.GROUP_SLUG,
            description=cls.GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text=cls.POST_TEXT,
            group=cls.group,
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # удаление временной папки после тестов
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # авторизованный пользователь
        self.user = User.objects.create_user(username=self.USER)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # авторизованный пользователь, автор поста
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.author)

    def test_create_post_form(self):
        """Валидная форма создает запись в Post"""
        posts_count = Post.objects.count()
        form_data = {
            'text': self.POST_TEXT,
            'group': self.GROUP_ID,
            'image': self.POST_IMAGE
        }
        response = self.authorized_client_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             reverse('posts:profile',
                                     kwargs={'username': self.AUTHOR}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        new_post = Post.objects.get(id=self.NEW_POST_ID)
        self.assertEqual(new_post.text, self.POST_TEXT)
        self.assertEqual(new_post.group.id, self.GROUP_ID)
        self.assertEqual(new_post.image, f'posts/{self.POST_IMAGE.name}')

    def test_edit_post_form(self):
        """Валидная форма изменяет запись в Post"""
        posts_count = Post.objects.count()
        form_data = {
            'text': self.POST_TEXT_EDITED,
            'group': self.GROUP_ID_EDITED,
            'image': self.POST_IMAGE_EDITED
        }
        response = self.authorized_client_author.post(
            reverse('posts:post_edit', kwargs={'pk': self.POST_ID}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             reverse('posts:post_detail',
                                     kwargs={'pk': self.POST_ID}))
        self.assertEqual(Post.objects.count(), posts_count)
        edited_post = Post.objects.get(id=self.POST_ID)
        self.assertEqual(edited_post.text, self.POST_TEXT_EDITED)
        self.assertIsNone(edited_post.group)
        self.assertEqual(edited_post.image,
                         f'posts/{self.POST_IMAGE_EDITED.name}')

    def test_add_comment_form(self):
        """Валидная форма добавляет комментарий к посту"""
        comments_count = self.post.comments.all().count()
        form_data = {
            'text': self.POST_COMMENT,
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'pk': self.POST_ID}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             reverse('posts:post_detail',
                                     kwargs={'pk': self.POST_ID}))
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        new_comment = self.post.comments.all()[0]
        self.assertEqual(new_comment.text, self.POST_COMMENT)
        self.assertEqual(new_comment.author.username, self.USER)
        self.assertEqual(new_comment.post.id, self.POST_ID)
