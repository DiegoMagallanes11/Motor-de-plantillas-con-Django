from django.db import models
from django.urls import reverse
from django.utils import timezone


class Category(models.Model):
    name = models.CharField("nombre", max_length=80, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField("descripción", blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "categoría"
        verbose_name_plural = "categorías"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("news:category", kwargs={"slug": self.slug})


class Author(models.Model):
    name = models.CharField("nombre", max_length=120)
    email = models.EmailField("correo", blank=True)
    bio = models.TextField("biografía", blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "autor"
        verbose_name_plural = "autores"

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField("título", max_length=200)
    slug = models.SlugField(unique=True)
    summary = models.TextField("resumen")
    body = models.TextField("cuerpo")
    featured_image = models.ImageField(
        "imagen destacada", upload_to="articles/%Y/%m/", blank=True
    )
    published_at = models.DateTimeField("fecha de publicación", default=timezone.now)
    is_published = models.BooleanField("publicado", default=True)
    author = models.ForeignKey(
        Author, verbose_name="autor", on_delete=models.PROTECT,
        related_name="articles",
    )
    categories = models.ManyToManyField(
        Category, verbose_name="categorías", related_name="articles"
    )

    class Meta:
        ordering = ["-published_at", "-pk"]
        verbose_name = "noticia"
        verbose_name_plural = "noticias"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("news:detail", kwargs={"slug": self.slug})
