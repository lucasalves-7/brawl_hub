from django.http import Http404
from django.shortcuts import render

from services import brawlers as catalog
from services import rankings as rank_svc
from services.brawler_art import (
    brawler_avatar,
    brawler_image,
    brawler_model_image,
    gadget_image,
    gear_image,
    player_icon_image,
    star_power_image,
)
from services.supercell_api import SupercellAPIError


def _attach_images(b: dict) -> dict:
    """Acrescenta as URLs de imagem (CDN) e o avatar gerado como fallback."""
    b["image"] = brawler_image(b["id"])
    b["model_image"] = brawler_model_image(b["id"])
    b["avatar"] = brawler_avatar(b["raw_name"], b["id"])

    for sp in b["star_powers"]:
        sp["image"] = star_power_image(sp["id"])
    for g in b["gadgets"]:
        g["image"] = gadget_image(g["id"])
    for gr in b["gears"]:
        gr["image"] = gear_image(gr["id"])
    return b


def catalog_list(request):
    """Catálogo global de Brawlers (Fase 5) — grade com busca no cliente."""
    try:
        brawlers = catalog.all_brawlers()
    except SupercellAPIError as exc:
        return render(
            request,
            "brawlers/catalog.html",
            {"error": {"title": "Erro ao consultar a Supercell", "message": exc.message}},
        )

    for b in brawlers:
        _attach_images(b)

    return render(
        request,
        "brawlers/catalog.html",
        {"brawlers": brawlers, "brawler_count": len(brawlers)},
    )


def brawler_detail(request, brawler_id: int):
    """Ficha global de um Brawler: o kit completo (acessórios) da API oficial."""
    # Garante o catálogo em cache antes de procurar (evita chamada extra).
    try:
        b = catalog.brawler_by_id(brawler_id)
    except SupercellAPIError as exc:
        return render(
            request,
            "brawlers/detail.html",
            {"error": {"title": "Erro ao consultar a Supercell", "message": exc.message}},
        )

    if b is None:
        raise Http404("Brawler não encontrado no catálogo.")

    _attach_images(b)

    # "Top mundial com este Brawler" (Fase 6) — degrada em silêncio se falhar.
    top: list[dict] = []
    country = request.GET.get("pais", "global")
    if not rank_svc.is_valid_country(country):
        country = "global"
    try:
        top = rank_svc.brawler_rankings(b["id"], country)
        for p in top:
            p["icon_image"] = player_icon_image(p["icon_id"])
    except SupercellAPIError:
        top = []

    return render(
        request,
        "brawlers/detail.html",
        {
            "b": b,
            "has_hypercharge": bool(b["hypercharges"]),
            "top_players": top,
            "top_country": country,
            "top_country_label": rank_svc.country_label(country),
            "countries": rank_svc.COUNTRIES,
        },
    )
