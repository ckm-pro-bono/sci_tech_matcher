from django.test import TestCase, tag, Client

from ...urls import urlpatterns


@tag('unittest')
class TestIndex(TestCase):
    url = '/'

    def setUp(self):
        self.client = Client()

    def test_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_template_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'main/index.html')
