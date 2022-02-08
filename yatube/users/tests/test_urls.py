from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()

URL_NAMES_TEMPLATES = {
    reverse('users:password_change'): 'users/password_change_form.html',
    reverse('users:password_change_done'): 'users/password_change_done.html',
    reverse('users:logout'): 'users/logged_out.html',
    reverse('users:signup'): 'users/signup.html',
    reverse('users:password_reset_form'): 'users/password_reset_form.html',
    reverse('users:password_reset_done'): 'users/password_reset_done.html',
    reverse('users:password_reset_confirm',
            kwargs={'uidb64': 'uidb64', 'token': 'token'}):
                'users/password_reset_confirm.html',
    reverse('users:password_reset_complete'):
        'users/password_reset_complete.html',
    reverse('users:login'): 'users/login.html',
}

USER = 'test-user'


class UsersURLTests(TestCase):
    def setUp(self):

        self.user = User.objects.create_user(username=USER)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_for_urls_exists_at_desired_location(self):
        """Проверка доступности адресов приложения users"""
        for address in URL_NAMES_TEMPLATES:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_uses_correct_template(self):
        """Проверка шаблонов страниц приложения users"""
        for address, template in URL_NAMES_TEMPLATES.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
