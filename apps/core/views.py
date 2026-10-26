from django.shortcuts import render


def home(request):
    """Página inicial do Brawl Hub (Fase 2)."""
    return render(request, "home.html")


def player_lookup(request, tag):
    """
    Rota de destino da busca por tag.

    Placeholder navegável: o dashboard real do jogador será construído na
    Fase 3 (dados demonstrativos) e conectado à API oficial na Fase 4.
    """
    return render(request, "players/lookup_placeholder.html", {"tag": tag})
