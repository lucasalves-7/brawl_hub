"""URLs raiz do Brawl Hub."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.players.urls")),
    path("", include("apps.brawlers.urls")),
    path("", include("apps.core.urls")),
]
