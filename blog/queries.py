"""Front-page queries and a shared rendering workload for accurate measurement."""
from .models import Article


def front_page_naive():
    return Article.objects.filter(is_published=True).order_by(
        "-published_at", "-id"
    )[:11]


def front_page():
    return Article.objects.filter(is_published=True).select_related(
        "author"
    ).prefetch_related("tags").order_by("-published_at", "-id")[:11]


def render_front_page(articles):
    return [
        {
            "id": article.id,
            "title": article.title,
            "author": article.author.name,
            "tags": [tag.name for tag in article.tags.all()],
        }
        for article in articles
    ]
