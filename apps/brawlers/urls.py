from django.urls import path

from . import views

app_name = "brawlers"

urlpatterns = [
    path("brawlers/", views.catalog_list, name="catalog"),
    path("brawlers/<int:brawler_id>/", views.brawler_detail, name="detail"),
]
