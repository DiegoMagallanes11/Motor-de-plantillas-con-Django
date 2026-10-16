"""Verified reference solutions prepared with Codex, not unaided student work."""
from datetime import datetime
from zoneinfo import ZoneInfo

from django.db.models import Count, Q

from blog.models import Article, Author, Category
from blog.queries import front_page


def question_1():
    boundary = datetime(2026, 10, 5, tzinfo=ZoneInfo("America/Lima"))
    return Article.objects.filter(is_published=True).filter(
        published_at__gte=boundary
    ).order_by("id")


def question_2():
    return Article.objects.filter(is_published=True).filter(
        author__profile__city="Lima", category__name="Tecnología"
    ).order_by("id")


def question_3():
    return Article.objects.filter(is_published=True).filter(
        Q(category__name="Tecnología") | Q(category__isnull=True)
    ).order_by("id")


def question_4():
    return Author.objects.filter(
        articles__is_published=True, articles__tags__name="django"
    ).distinct().order_by("id")


def question_5():
    return Article.objects.annotate(
        n_comments=Count("comments", distinct=True),
        n_tags=Count("tags", distinct=True),
    ).order_by("id")


def question_6():
    return Author.objects.exclude(
        articles__comments__is_approved=True
    ).order_by("id")


def question_7():
    return Category.objects.annotate(
        n_articles=Count("articles", filter=Q(articles__is_published=True))
    ).filter(n_articles__gte=2).order_by("id")


def question_8():
    return front_page()
