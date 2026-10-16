"""Isolated practice models for the adapted Lab 07 dataset."""
from django.db import models


class Author(models.Model):
    name = models.CharField("nombre", max_length=120)
    email = models.EmailField("correo", blank=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "autor de práctica"
        verbose_name_plural = "autores de práctica"

    def __str__(self):
        return self.name


class Profile(models.Model):
    author = models.OneToOneField(
        Author, on_delete=models.CASCADE, related_name="profile"
    )
    city = models.CharField("ciudad", max_length=80)
    bio = models.TextField("biografía", blank=True)

    def __str__(self):
        return f"{self.author.name} — {self.city}"


class Category(models.Model):
    name = models.CharField("nombre", max_length=80, unique=True)

    class Meta:
        ordering = ["id"]
        verbose_name_plural = "categorías de práctica"

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField("nombre", max_length=50, unique=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField("título", max_length=180)
    author = models.ForeignKey(
        Author, on_delete=models.PROTECT, related_name="articles"
    )
    category = models.ForeignKey(
        Category, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="articles",
    )
    tags = models.ManyToManyField(Tag, related_name="articles", blank=True)
    published_at = models.DateTimeField("fecha de publicación")
    is_published = models.BooleanField("publicado", default=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "artículo de práctica"
        verbose_name_plural = "artículos de práctica"

    def __str__(self):
        return self.title


class Comment(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="comments"
    )
    author_name = models.CharField("nombre", max_length=100)
    body = models.TextField("contenido")
    is_approved = models.BooleanField("aprobado", default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"Comment {self.pk} on article {self.article_id}"
