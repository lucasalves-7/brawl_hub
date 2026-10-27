from django.http import Http404
from django.shortcuts import render

from services import rankings as rank_svc
from services.brawler_art import player_icon_image
from services.supercell_api import SupercellAPIError


def _badge_image(badge_id: int | None) -> str | None:
    """Escudo do clube no CDN público (Brawlify)."""
    if not badge_id:
        return None
    return f"https://cdn.brawlify.com/club-badges/regular/{badge_id}.png"


def _rankings_view(request):
    """Ranking de Jogores/Clubes com seletor de região (Fase 6)."""
    kind = request.GET.get("aba", "jogadores")
    if kind not in ("jogadores", "clubes"):
        kind = "jogadores"

    country = request.GET.get("pais", "global")
    if not rank_svc.is_valid_country(country):
        country = "global"

    context = {
        "kind": kind,
        "country": country,
        "country_label": rank_svc.country_label(country),
        "countries": rank_svc.COUNTRIES,
    }

    try:
        if kind == "clubes":
            clubs = rank_svc.club_rankings(country)
            for c in clubs:
                c["badge_image"] = _badge_image(c["badge_id"])
            context["clubs"] = clubs
        else:
            players = rank_svc.player_rankings(country)
            for p in players:
                p["icon_image"] = player_icon_image(p["icon_id"])
            context["players"] = players
    except SupercellAPIError as exc:
        context["error"] = {
            "title": "Erro ao consultar a Supercell",
            "message": exc.message,
        }

    return render(request, "rankings/rankings.html", context)


def rankings(request):
    """Página única de rankings, com abas Jogadores/Clubes."""
    return _rankings_view(request)


def club_detail(request, tag: str):
    """Página de um clube: informações + membros (Fase 6)."""
    tag = (tag or "").strip()
    if not tag:
        raise Http404("Clube não encontrado.")

    try:
        club = rank_svc.club_detail(tag)
    except SupercellAPIError as exc:
        if exc.status == 404:
            raise Http404("Clube não encontrado.")
        return render(
            request,
            "rankings/club.html",
            {"error": {"title": "Erro ao consultar a Supercell", "message": exc.message}},
        )

    club["badge_image"] = _badge_image(club["badge_id"])
    club["type_label"] = rank_svc.club_type_label(club["type"])
    for m in club["members"]:
        m["icon_image"] = player_icon_image(m["icon_id"])
        m["role_label"] = rank_svc.role_label(m["role"])

    return render(request, "rankings/club.html", {"club": club})
