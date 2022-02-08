from django.test import Client, TestCase
from django.urls import reverse


class AboutPagesTests(TestCase):
    def setUp(self):
        # неавторизованный пользователь
        self.guest_client = Client()

    def test_about_pages_uses_correct_template(self):
        """Адрес вида namespace:name использует соответствующий шаблон"""
        page_names_templates = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }
        for reverse_name, template in page_names_templates.items():
            with self.subTest(template=template):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
