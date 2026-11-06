from rest_framework.test import APITestCase

from quiz.models import Choice, Question
from .helpers import seed


class ChoiceInvariantTests(APITestCase):
    def setUp(self):
        person, self.agent = seed()
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {person}")
        self.question = Question.objects.first()

    def test_router_exposes_three_resources(self):
        self.assertEqual(set(self.client.get("/api/").json()), {
            "exams", "questions", "choices",
        })

    def test_create_wrong_option_and_patch_and_delete_it(self):
        response = self.client.post("/api/choices/", {
            "question": self.question.pk, "text": "Otra", "is_correct": False,
        })
        self.assertEqual(response.status_code, 201)
        url = f"/api/choices/{response.data['id']}/"
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertEqual(self.client.patch(url, {"text": "Cambio"}).status_code, 200)
        self.assertEqual(self.client.delete(url).status_code, 204)

    def test_cannot_create_second_correct_option(self):
        response = self.client.post("/api/choices/", {
            "question": self.question.pk, "text": "Otra", "is_correct": True,
        })
        self.assertEqual(response.status_code, 400)

    def test_cannot_delete_correct_option_or_unmark_it(self):
        choice = self.question.choices.get(is_correct=True)
        url = f"/api/choices/{choice.pk}/"
        self.assertEqual(self.client.delete(url).status_code, 400)
        self.assertEqual(self.client.patch(url, {"is_correct": False}).status_code, 400)
        self.assertTrue(Choice.objects.get(pk=choice.pk).is_correct)

    def test_nested_patch_invalid_data_is_atomic(self):
        original = self.question.text
        response = self.client.patch(f"/api/questions/{self.question.pk}/", {
            "text": "No debe guardarse",
            "choices": [{"text": "a", "is_correct": False},
                        {"text": "b", "is_correct": False}],
        }, format="json")
        self.assertEqual(response.status_code, 400)
        self.question.refresh_from_db()
        self.assertEqual(self.question.text, original)

    def test_invalid_filter_returns_400(self):
        self.assertEqual(self.client.get("/api/questions/?exam=no").status_code, 400)

    def test_agent_cannot_delete_a_choice(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.agent}")
        choice = self.question.choices.filter(is_correct=False).first()
        self.assertEqual(self.client.delete(f"/api/choices/{choice.pk}/").status_code, 403)

    def test_partial_nested_replacement_requires_text(self):
        response = self.client.patch(f"/api/questions/{self.question.pk}/", {
            "choices": [{"is_correct": True}, {"text": "b", "is_correct": False}],
        }, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.question.choices.count(), 4)
