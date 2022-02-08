from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()

USER = 'test-user'


class UserPagesTests(TestCase):
    def setUp(self):
        # авторизованный пользователь
        self.user = User.objects.create_user(username=USER)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_user_pages_uses_correct_template(self):
        """Адрес вида namespace:name использует соответствующий шаблон"""
        page_names_templates = {
            reverse('users:password_change'):
                'users/password_change_form.html',
            reverse('users:password_change_done'):
                'users/password_change_done.html',
            reverse('users:logout'):
                'users/logged_out.html',
            reverse('users:signup'):
                'users/signup.html',
            reverse('users:password_reset_form'):
                'users/password_reset_form.html',
            reverse('users:password_reset_done'):
                'users/password_reset_done.html',
            reverse('users:password_reset_confirm',
                    kwargs={'uidb64': 'uidb64', 'token': 'token'}):
                'users/password_reset_confirm.html',
            reverse('users:password_reset_complete'):
                'users/password_reset_complete.html',
            reverse('users:login'):
                'users/login.html',
        }
        for reverse_name, template in page_names_templates.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_signup_page_show_correct_context(self):
        """Шаблон signup сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse(
            'users:signup'))
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
            'password1': forms.fields.CharField,
            'password2': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                # проверка типа поля формы
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
                # проверка начальных значений формы
                self.assertIsNone(form_field.initial)
