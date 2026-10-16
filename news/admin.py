from django.contrib import admin

from .models import Article, Author, Category

admin.site.site_header = "Administración de Pulso"
admin.site.site_title = "Pulso Admin"
admin.site.index_title = "Gestión editorial"


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "published_at", "is_published")
    list_filter = ("is_published", "categories", "author", "published_at")
    search_fields = ("title", "summary", "body")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("categories",)
    date_hierarchy = "published_at"
    list_select_related = ("author",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    list_filter = ("name",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "email")
    list_filter = ("name",)
    search_fields = ("name", "email", "bio")
