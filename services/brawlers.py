"""
Catálogo global de Brawlers (Fase 5).

A API da Supercell expõe dois pontos de leitura, ambos SOMENTE com o kit
(acessórios) — não trazem combate, classe ou raridade:

- GET /brawlers           -> lista inteira do catálogo (paginação opcional)
- GET /brawlers/{id}      -> um Brawler específico

O catálogo muda só a cada temporada, então usamos cache longo (TTL_STATIC),
reduzindo muito as consultas à API.
"""
from __future__ import annotations

from services import cache as hub_cache
from services.supercell_api import SupercellClient


def _clean_accessories(items: list[dict] | None) -> list[dict]:
    """Reduz um acessório (Star Power, Gadget, Gear...) aos campos da UI."""
    out = []
    for it in items or []:
        if not isinstance(it, dict):
            continue
        entry = {"id": it.get("id"), "name": (it.get("name") or "").title()}
        if it.get("level") is not None:
            entry["level"] = it["level"]
        out.append(entry)
    return out


def normalize_catalog_brawler(raw: dict) -> dict:
    """Normaliza um item do catálogo aos campos que a ficha usa."""
    name = (raw.get("name") or "").title()
    b = {
        "id": raw.get("id"),
        "name": name,
        "raw_name": raw.get("name", ""),
        "star_powers": _clean_accessories(raw.get("starPowers")),
        "hypercharges": _clean_accessories(raw.get("hyperCharges")),
        "gadgets": _clean_accessories(raw.get("gadgets")),
        "gears": _clean_accessories(raw.get("gears")),
    }
    # Grupo B (calculado, rotulado): total de acessórios do kit.
    b["accessory_count"] = (
        len(b["star_powers"]) + len(b["hypercharges"])
        + len(b["gadgets"]) + len(b["gears"])
    )
    return b


def _fetch_catalog() -> list[dict]:
    """Busca o catálogo inteiro, seguindo a paginação se houver."""
    client = SupercellClient()
    items: list[dict] = []
    after: str | None = None

    while True:
        data = client.brawlers_catalog(limit=500, after=after)
        page = data.get("items", []) if isinstance(data, dict) else []
        items.extend(page)

        # Só continua se a API devolver um próximo cursor.
        cursors = (data.get("paging") or {}).get("cursors", {}) if isinstance(data, dict) else {}
        after = cursors.get("after")
        if not after or not page:
            break

    return items


def all_brawlers() -> list[dict]:
    """Catálogo completo (com cache), normalizado e ordenado por nome."""
    raw_items = hub_cache.cached(
        "brawlers:catalog", hub_cache.TTL_STATIC, _fetch_catalog
    )
    brawlers = [normalize_catalog_brawler(r) for r in raw_items]
    brawlers.sort(key=lambda b: b["name"])
    return brawlers


def brawler_by_id(brawler_id: int) -> dict | None:
    """
    Um Brawler do catálogo pelo id. Devolve None se não existir.

    Busca do catálogo em cache (sem chamada extra à API por visita).
    """
    for b in all_brawlers():
        if b["id"] == brawler_id:
            return b
    return None



