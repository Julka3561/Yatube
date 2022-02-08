from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

URL_NAMES_TEMPLATES = {
    reverse('about:author'): 'about/author.html',
    reverse('about:tech'): 'about/tech.html',
}


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_url_exists_at_desired_location(self):
        """Проверка доступности адресов приложения about"""
        for address in URL_NAMES_TEMPLATES:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_uses_correct_template(self):
        """Проверка шаблонов страниц приложения about"""
        for address, template in URL_NAMES_TEMPLATES.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
