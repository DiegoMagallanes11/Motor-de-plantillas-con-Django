from datetime import timedelta
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Article, Author, Category


class PortalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = Author.objects.create(name="Test Author", bio="Test biography")
        cls.category = Category.objects.create(name="Tecnología", slug="tecnologia")
        cls.empty_category = Category.objects.create(name="Vacía", slug="vacia")
        cls.article = Article.objects.create(
            title="Published story", slug="published-story", author=cls.author,
            summary=" ".join(f"word{number}" for number in range(30)),
            body="<strong>Texto de prueba</strong>\nSecond line",
            published_at=timezone.now() - timedelta(days=1),
        )
        cls.article.categories.add(cls.category)
        cls.other = Article.objects.create(
            title="Other category", slug="other-category", author=cls.author,
            summary="Other summary", body="Other body",
        )
        cls.draft = Article.objects.create(
            title="Draft story", slug="draft-story", author=cls.author,
            summary="Draft", body="Draft", is_published=False,
        )
        cls.future = Article.objects.create(
            title="Future story", slug="future-story", author=cls.author,
            summary="Future", body="Future",
            published_at=timezone.now() + timedelta(days=2),
        )
        cls.admin_user = get_user_model().objects.create_superuser(
            "test-admin", password="test-only-password"
        )

    def test_home_uses_inheritance_card_and_filters(self):
        response = self.client.get(reverse("news:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "base.html")
        self.assertTemplateUsed(response, "news/_article_card.html")
        self.assertContains(response, "Published story")
        self.assertContains(response, "word21")
        self.assertNotContains(response, "word22")
        self.assertContains(response, "/static/news/css/styles.css")
        self.assertContains(response, self.article.get_absolute_url())
        self.assertContains(response, self.category.get_absolute_url())
        self.assertNotContains(response, "Draft story")
        self.assertNotContains(response, "Future story")

    def test_detail_escapes_html_and_displays_relations(self):
        response = self.client.get(self.article.get_absolute_url())
        self.assertContains(response, "&lt;strong&gt;Texto de prueba&lt;/strong&gt;")
        self.assertNotContains(response, "<strong>Texto de prueba</strong>")
        self.assertContains(response, "Test Author")
        self.assertContains(response, "Test biography")
        self.assertContains(response, "Tecnología")

    def test_category_filters_and_reuses_card(self):
        response = self.client.get(self.category.get_absolute_url())
        self.assertContains(response, "Published story")
        self.assertNotContains(response, "Other category")
        self.assertTemplateUsed(response, "news/_article_card.html")

    def test_empty_category(self):
        response = self.client.get(self.empty_category.get_absolute_url())
        self.assertContains(response, "Aún no hay noticias en esta categoría")

    def test_empty_home(self):
        Article.objects.all().delete()
        response = self.client.get(reverse("news:home"))
        self.assertContains(response, "No hay noticias publicadas por el momento.")

    def test_drafts_future_and_missing_objects_return_404(self):
        for slug in (self.draft.slug, self.future.slug, "missing"):
            self.assertEqual(self.client.get(reverse("news:detail", args=[slug])).status_code, 404)
        self.assertEqual(self.client.get(reverse("news:category", args=["missing"])).status_code, 404)

    def test_admin_edit_reaches_portal(self):
        self.client.force_login(self.admin_user)
        response = self.client.post(
            reverse("admin:news_article_change", args=[self.article.pk]),
            {"title": "Updated from administrator", "slug": self.article.slug,
             "summary": self.article.summary, "body": self.article.body,
             "author": self.author.pk, "categories": [self.category.pk],
             "published_at_0": "2026-01-01", "published_at_1": "09:00:00",
             "is_published": "on", "_save": "Save"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertContains(self.client.get(self.article.get_absolute_url()), "Updated from administrator")

    def test_admin_search_and_category_filter(self):
        self.client.force_login(self.admin_user)
        url = reverse("admin:news_article_changelist")
        response = self.client.get(url, {"q": "Published story"})
        self.assertEqual(list(response.context["cl"].queryset), [self.article])
        response = self.client.get(url, {"categories__id__exact": self.category.pk})
        self.assertEqual(list(response.context["cl"].queryset), [self.article])

    def test_admin_requires_login(self):
        response = self.client.get(reverse("admin:news_article_changelist"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.url)

    def test_author_with_articles_is_protected(self):
        from django.db.models.deletion import ProtectedError

        with self.assertRaises(ProtectedError):
            self.author.delete()
