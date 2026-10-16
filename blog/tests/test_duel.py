from django.db.models import QuerySet
from django.test import TestCase
from django.urls import reverse

from blog.duel import team
from blog.duel.verifier import measure_front_page, run_duel
from blog.models import Article, Author, Category, Comment, Profile, Tag
from blog.queries import front_page, front_page_naive, render_front_page
from blog.seed import seed_blog
from news.models import Article as NewsArticle
from news.models import Author as NewsAuthor


class DuelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        seed_blog()

    def test_all_eight_reference_solutions_match_fixed_keys_and_budgets(self):
        results = run_duel()
        self.assertEqual([row["status"] for row in results], ["accepted"] * 8)
        self.assertEqual([row["queries"] for row in results], [1] * 7 + [2])
        for number in range(1, 9):
            with self.subTest(question=number):
                self.assertIsInstance(getattr(team, f"question_{number}")(), QuerySet)

    def test_deliberately_faulty_candidates_are_detected(self):
        results = run_duel("ai")
        self.assertEqual([row["status"] for row in results], [
            "wrong_result", "error", "wrong_result", "wrong_result",
            "wrong_result", "wrong_result", "wrong_result", "expensive",
        ])
        self.assertIn("FieldError", results[1]["error"])
        self.assertEqual(results[7]["queries"], 23)
        self.assertEqual(results[4]["actual"][0], [1, 8, 8])

    def test_optimization_preserves_all_rendered_fields(self):
        result = measure_front_page()
        self.assertEqual(result["before"]["queries"], 23)
        self.assertEqual(result["after"]["queries"], 2)
        self.assertTrue(result["same_payload"])

    def test_query_count_stays_constant_when_articles_grow(self):
        original = Article.objects.get(pk=1)
        for number in range(13, 25):
            article = Article.objects.create(
                id=number, title=f"Extra {number}", author=original.author,
                category=original.category, published_at=original.published_at,
            )
            article.tags.set([1, 2])
        naive = front_page_naive().query.clone()
        # Remove the display limit to measure the complete growing dataset.
        naive.clear_limits()
        naive_queryset = Article.objects.all()
        naive_queryset.query = naive
        optimized = Article.objects.filter(is_published=True).select_related(
            "author"
        ).prefetch_related("tags")
        with self.assertNumQueries(47):
            before = render_front_page(naive_queryset)
        with self.assertNumQueries(2):
            after = render_front_page(optimized.order_by("-published_at", "-id"))
        self.assertEqual(before, after)

    def test_reverse_relation_returns_authors_without_articles(self):
        ids = list(team.question_6().values_list("id", flat=True))
        self.assertIn(7, ids)
        self.assertNotIn(1, ids)

    def test_nullable_category_and_zero_relations_are_preserved(self):
        self.assertIn(9, list(team.question_3().values_list("id", flat=True)))
        article = team.question_5().get(pk=9)
        self.assertEqual((article.n_comments, article.n_tags), (1, 0))

    def test_seed_is_reproducible_and_preserves_news(self):
        author = NewsAuthor.objects.create(name="Preserved author")
        NewsArticle.objects.create(
            title="Preserved Lab 06", slug="preserved-lab06", author=author,
            summary="Unchanged", body="Unchanged",
        )
        news_before = NewsArticle.objects.count()
        counts = seed_blog()
        self.assertEqual(counts, {
            "authors": 7, "profiles": 7, "articles": 12, "published": 11,
            "categories": 4, "tags": 5, "comments": 15,
        })
        self.assertEqual(NewsArticle.objects.count(), news_before)
        self.assertEqual(Comment.objects.get(pk=4).article_id, 1)

    def test_dashboard_is_read_only_and_displays_verified_results(self):
        response = self.client.get(reverse("blog:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ocho preguntas")
        self.assertContains(response, "approval_required")
        self.assertContains(response, "23")
        self.assertEqual(Comment.objects.count(), 15)
        self.assertEqual(Article.objects.count(), 12)
        self.assertEqual(self.client.post(reverse("blog:dashboard")).status_code, 405)

    def test_dashboard_handles_an_unseeded_database(self):
        Article.objects.all().delete()
        response = self.client.get(reverse("blog:dashboard"))
        self.assertEqual(response.status_code, 200)
