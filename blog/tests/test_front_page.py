from django.test import TestCase

from blog.queries import front_page, render_front_page
from blog.seed import seed_blog


class FrontPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        seed_blog()

    def test_front_page_uses_two_queries(self):
        with self.assertNumQueries(2):
            rows = render_front_page(front_page())
        self.assertEqual(len(rows), 11)
        self.assertEqual(rows[0]["id"], 11)
