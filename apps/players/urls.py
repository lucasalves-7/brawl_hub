from django.urls import path

from . import views

app_name = "players"

urlpatterns = [
    path("perfil/<str:tag>/", views.player_profile, name="profile"),
    path("exemplo/", views.top_example, name="example"),
]
