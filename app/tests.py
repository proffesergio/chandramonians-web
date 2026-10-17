from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from app.models import NewsArticle


class PublicPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.article = NewsArticle.objects.create(
            title='School news', slug='school-news', excerpt='Latest news',
            content='News content', is_published=True,
        )

    @patch('webapp.Public_Views._fetch_rss_headlines', return_value=[])
    def test_public_pages_render(self, rss):
        # Exercise the view, template inheritance, includes, and URL tags together.
        pages = [
            ('landing', 'home.html'),
            ('about', 'about.html'),
            ('news_list', 'news_list.html'),
            ('events', 'events.html'),
            ('gallery', 'gallery.html'),
            ('contact', 'contact.html'),
            ('public_directory', 'alumni_directory.html'),
            ('public_members', 'members.html'),
        ]
        for name, template in pages:
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, f'pages/{template}')
                self.assertTemplateUsed(response, 'public_base.html')

    def test_published_news_detail_renders(self):
        response = self.client.get(reverse('news_detail', args=[self.article.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/news_detail.html')
        self.assertContains(response, self.article.title)
