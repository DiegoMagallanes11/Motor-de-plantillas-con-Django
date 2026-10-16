from django.urls import path

from . import views

app_name = "news"
urlpatterns = [
    path("", views.home, name="home"),
    path("noticias/<slug:slug>/", views.detail, name="detail"),
    path("categorias/<slug:slug>/", views.category, name="category"),
]
