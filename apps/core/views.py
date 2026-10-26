from django.shortcuts import render


def home(request):
    """Página inicial do Brawl Hub (Fase 2)."""
    return render(request, "home.html")
