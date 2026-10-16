"""Deliberately faulty teaching candidates authored by Codex for comparison.

These examples are not an authentic transcript from a teacher-provided model.
They must never be interpreted as records of spontaneous AI failures.
"""
from datetime import datetime
from zoneinfo import ZoneInfo

from django.db.models import Count

from blog.models import Article, Author, Category
from blog.queries import front_page_naive


def question_1():
    boundary = datetime(2026, 10, 5, tzinfo=ZoneInfo("America/Lima"))
    return Article.objects.filter(
        is_published=True, published_at__gt=boundary
    ).order_by("id")


def question_2():
    return Article.objects.filter(
        is_published=True, author__city="Lima", category__name="Tecnología"
    ).order_by("id")


def question_3():
    return Article.objects.filter(
        is_published=True, category__name="Tecnología"
    ).order_by("id")


def question_4():
    return Author.objects.filter(
        articles__is_published=True, articles__tags__name="django"
    ).order_by("id")


def question_5():
    return Article.objects.annotate(
        n_comments=Count("comments"), n_tags=Count("tags")
    ).order_by("id")


def question_6():
    return Author.objects.filter(
        articles__comments__is_approved=False
    ).distinct().order_by("id")


def question_7():
    return Category.objects.annotate(
        n_articles=Count("articles")
    ).filter(n_articles__gte=2).order_by("id")


def question_8():
    return front_page_naive()
