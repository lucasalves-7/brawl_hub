from django.shortcuts import redirect, render
from django.urls import reverse

from services import cache as hub_cache
from services import statistics as stats
from services.brawler_art import brawler_avatar
from services.supercell_api import (
    SupercellAPIError,
    SupercellClient,
    is_valid_tag,
    normalize_tag,
)


def _load_player_data(tag: str) -> tuple[dict, list[dict]]:
    """Busca perfil e battlelog, com cache. Propaga SupercellAPIError."""
    client = SupercellClient()
    raw = hub_cache.cached(
        f"player:{tag}", hub_cache.TTL_PLAYER, lambda: client.player(tag)
    )
    battlelog = hub_cache.cached(
        f"battlelog:{tag}", hub_cache.TTL_BATTLELOG, lambda: client.battlelog(tag)
    )
    return raw, battlelog


def player_profile(request, tag: str):
    """Dashboard do jogador com dados reais da API (Fase 4)."""
    tag = normalize_tag(tag)
    context = {"requested_tag": tag}

    if not is_valid_tag(tag):
        context["error"] = {
            "title": "Tag inválida",
            "message": "Use de 3 a 14 caracteres, apenas com 0, 2, 8, 9, P, Y, L, Q, G, R, J, C, U e V.",
        }
        return render(request, "players/profile.html", context)

    try:
        raw, battlelog = _load_player_data(tag)
    except SupercellAPIError as exc:
        context["error"] = {
            "title": {
                404: "Jogador não encontrado",
                403: "Sem acesso à API",
                429: "Muitas consultas",
            }.get(exc.status, "Erro ao consultar a Supercell"),
            "message": exc.message,
        }
        return render(request, "players/profile.html", context)

    player = stats.normalize_player(raw)
    player["avatar"] = brawler_avatar(player["name"])

    brawlers = [stats.normalize_brawler(b) for b in raw.get("brawlers", [])]
    for b in brawlers:
        b["avatar"] = brawler_avatar(b["raw_name"], b["id"])

    distribution = stats.trophy_distribution(brawlers, top=10)
    perf = stats.recent_performance(battlelog, player["tag"])

    context.update(
        {
            "player": player,
            "brawlers": brawlers,
            "distribution": distribution,
            "perf": perf,
            "brawler_count": stats.brawler_count(brawlers),
        }
    )
    return render(request, "players/profile.html", context)


def top_example(request):
    """Redireciona para o perfil do líder global — o botão 'ver um exemplo'."""
    client = SupercellClient()
    try:
        items = hub_cache.cached(
            "rankings:global:players",
            hub_cache.TTL_RANKINGS,
            lambda: client.rankings("players", "global"),
        )
        top_tag = items[0].get("tag") if items else None
    except SupercellAPIError:
        top_tag = None

    if top_tag:
        return redirect(
            reverse("players:profile", kwargs={"tag": top_tag.lstrip("#")})
        )
    return redirect("core:home")
