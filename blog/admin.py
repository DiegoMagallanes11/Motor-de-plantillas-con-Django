from django.contrib import admin

from .models import Article, Author, Category, Comment, Profile, Tag


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "category", "is_published")
    list_filter = ("is_published", "category", "tags")
    search_fields = ("title", "author__name")
    list_select_related = ("author", "category")
    filter_horizontal = ("tags",)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email")
    search_fields = ("name",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "article", "author_name", "is_approved")
    list_filter = ("is_approved",)
    search_fields = ("body",)
    list_select_related = ("article",)


admin.site.register((Profile, Category, Tag))
