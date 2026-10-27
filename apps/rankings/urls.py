from django.urls import path

from . import views

app_name = "rankings"

urlpatterns = [
    path("rankings/", views.rankings, name="rankings"),
    path("clube/<str:tag>/", views.club_detail, name="club"),
]
