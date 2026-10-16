from .models import Category


def navigation(request):
    return {"navigation_categories": Category.objects.all()}
