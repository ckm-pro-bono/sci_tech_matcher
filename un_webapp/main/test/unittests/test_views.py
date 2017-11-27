from django.test import TestCase, tag, RequestFactory

from ...views import IndexView


@tag('unittest')
class TestIndexView(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.view = IndexView

    def test_My_Searches_in_template(self):
        request = self.factory.get('/')
        response = self.view.as_view()(request).render()
        self.assertIn(bytearray('UNOM', 'utf-8'), response.content)
