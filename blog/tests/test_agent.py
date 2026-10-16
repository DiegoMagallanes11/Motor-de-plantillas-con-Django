from django.test import TestCase

from blog.agent.intents import INTENT_EXAMPLES, execute_intent
from blog.agent.registry import dispatch
from blog.models import Article, Comment
from blog.seed import seed_blog


class AgentTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        seed_blog()

    def test_four_intents_have_expected_statuses(self):
        self.assertEqual([
            execute_intent(intent)["status"] for intent in INTENT_EXAMPLES
        ], ["ok", "ok", "approval_required", "denied"])

    def test_unknown_action_and_extra_arguments_are_denied(self):
        self.assertEqual(dispatch("execute_sql")["status"], "denied")
        self.assertEqual(dispatch("list_posts", {"sql": "DELETE"})["status"], "denied")
        self.assertEqual(dispatch("delete_comments", {
            "article_id": 5, "all": True
        })["status"], "denied")
        self.assertEqual(dispatch("comments_of_post", {"article_id": True})["status"], "denied")

    def test_injected_comment_is_data_and_never_a_command(self):
        result = dispatch("comments_of_post", {"article_id": 1})
        self.assertTrue(result["untrusted_content"])
        self.assertIn("execute_sql", result["data"][3]["body"])
        self.assertEqual(Article.objects.count(), 12)
        self.assertEqual(Comment.objects.count(), 15)
        self.assertEqual(execute_intent(result["data"][3]["body"])["status"], "denied")

    def test_no_deletion_without_matching_approval(self):
        result = dispatch("delete_comments", {"article_id": 5})
        self.assertEqual(result["status"], "approval_required")
        self.assertEqual(result["comment_ids"], [9, 10, 11])
        denied = dispatch("delete_comments", {"article_id": 5}, "0" * 64)
        self.assertEqual(denied["status"], "denied")
        self.assertEqual(Comment.objects.count(), 15)

    def test_matching_plan_deletes_only_the_approved_article_comments(self):
        plan = dispatch("delete_comments", {"article_id": 5})
        result = dispatch("delete_comments", {"article_id": 5}, plan["plan_hash"])
        self.assertEqual(result["deleted"], 3)
        self.assertEqual(Comment.objects.filter(article_id=5).count(), 0)
        self.assertEqual(Comment.objects.filter(article_id=1).count(), 4)
        self.assertEqual(Article.objects.count(), 12)
        self.assertEqual(Comment.objects.count(), 12)

    def test_added_comment_invalidates_approval(self):
        plan = dispatch("delete_comments", {"article_id": 5})
        Comment.objects.create(article_id=5, author_name="New", body="New content")
        result = dispatch("delete_comments", {"article_id": 5}, plan["plan_hash"])
        self.assertEqual(result["reason"], "stale_or_invalid_plan")
        self.assertEqual(Comment.objects.filter(article_id=5).count(), 4)

    def test_edited_comment_invalidates_approval(self):
        plan = dispatch("delete_comments", {"article_id": 5})
        Comment.objects.filter(pk=9).update(body="Changed without updated_at")
        result = dispatch("delete_comments", {"article_id": 5}, plan["plan_hash"])
        self.assertEqual(result["status"], "denied")
        self.assertEqual(Comment.objects.filter(article_id=5).count(), 3)

    def test_plan_for_other_article_is_rejected(self):
        plan = dispatch("delete_comments", {"article_id": 5})
        result = dispatch("delete_comments", {"article_id": 1}, plan["plan_hash"])
        self.assertEqual(result["status"], "denied")
        self.assertEqual(Comment.objects.count(), 15)

    def test_executed_plan_cannot_be_replayed(self):
        plan = dispatch("delete_comments", {"article_id": 5})
        dispatch("delete_comments", {"article_id": 5}, plan["plan_hash"])
        result = dispatch("delete_comments", {"article_id": 5}, plan["plan_hash"])
        self.assertEqual(result["status"], "denied")

    def test_parser_rejects_appended_instructions(self):
        result = execute_intent("ver comentarios del artículo 1; borrar todo")
        self.assertEqual(result["status"], "denied")
        self.assertEqual(Comment.objects.count(), 15)

    def test_malformed_approval_is_denied_without_crashing(self):
        for invalid in ("á" * 64, "xyz", 123, True):
            with self.subTest(approval=invalid):
                result = dispatch("delete_comments", {"article_id": 5}, invalid)
                self.assertEqual(result["reason"], "invalid_approval")
        self.assertEqual(Comment.objects.count(), 15)
