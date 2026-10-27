from django.http import Http404
from django.shortcuts import render

from services import brawlers as catalog
from services.brawler_art import (
    brawler_avatar,
    brawler_image,
    brawler_model_image,
    gadget_image,
    gear_image,
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

    return render(
        request,
        "brawlers/detail.html",
        {"b": b, "has_hypercharge": bool(b["hypercharges"])},
    )
