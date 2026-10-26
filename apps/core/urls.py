from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("perfil/<str:tag>/", views.player_lookup, name="player_lookup"),
]
