"""
Rankings e Clubes (Fase 6).

Endpoints da API usados:
- /rankings/{país}/players   -> top de jogadores
- /rankings/{país}/clubs      -> top de clubes
- /rankings/{país}/brawlers/{id} -> top de jogadores por um Brawler
- /clubs/{tag}                -> um clube (já traz os membros)

Importante: a API NÃO tem o endpoint `locations` (devolve 404), então não dá
para montar a lista de regiões dinamicamente. Usamos uma lista CURADA de
códigos que foram verificados como válidos.

Rankings mudam pouco -> cache longo (TTL_RANKINGS), reduzindo chamadas à API.
"""
from __future__ import annotations

from services import cache as hub_cache
from services.supercell_api import SupercellClient

# Regiões verificadas (código da API -> rótulo para a interface).
# O endpoint `locations` é 404, então esta lista é curada à mão.
COUNTRIES = [
    ("global", "Global"),
    ("br", "Brasil"),
    ("us", "Estados Unidos"),
    ("mx", "México"),
    ("ca", "Canadá"),
    ("eu", "Europa"),
    ("es", "Espanha"),
    ("fr", "França"),
    ("it", "Itália"),
    ("de", "Alemanha"),
    ("jp", "Japão"),
    ("kr", "Coreia"),
]

COUNTRY_LABELS = dict(COUNTRIES)


def country_label(code: str | None) -> str:
    """Rótulo amigável para um código de região (devolve o próprio código se desconhecido)."""
    return COUNTRY_LABELS.get(code or "global", (code or "global").upper())


def is_valid_country(code: str | None) -> bool:
    return (code or "global") in COUNTRY_LABELS


def _safe_name(raw: str | None) -> str:
    return (raw or "").strip() or "Sem nome"


def normalize_player_ranking(item: dict) -> dict:
    """Um item do ranking de jogadores, reduzido ao que a UI usa."""
    club = item.get("club") or {}
    return {
        "tag": item.get("tag", ""),
        "name": _safe_name(item.get("name")),
        "trophies": item.get("trophies", 0),
        "rank": item.get("rank", 0),
        "icon_id": (item.get("icon") or {}).get("id"),
        "club_name": club.get("name"),
    }


def normalize_club_ranking(item: dict) -> dict:
    """Um item do ranking de clubes, reduzido ao que a UI usa."""
    return {
        "tag": item.get("tag", ""),
        "name": _safe_name(item.get("name")),
        "trophies": item.get("trophies", 0),
        "rank": item.get("rank", 0),
        "badge_id": item.get("badgeId"),
        "member_count": item.get("memberCount", 0),
    }


def normalize_member(item: dict) -> dict:
    """Um membro do clube (da página do clube)."""
    return {
        "tag": item.get("tag", ""),
        "name": _safe_name(item.get("name")),
        "trophies": item.get("trophies", 0),
        "role": item.get("role", "member"),
        "icon_id": (item.get("icon") or {}).get("id"),
    }


def normalize_club(raw: dict) -> dict:
    """Um clube completo (da página do clube)."""
    members = [normalize_member(m) for m in raw.get("members") or []]
    # Membros já vêm ordenados pela API, mas garantimos por troféus.
    members.sort(key=lambda m: m["trophies"], reverse=True)
    return {
        "tag": raw.get("tag", ""),
        "name": _safe_name(raw.get("name")),
        "description": (raw.get("description") or "").strip(),
        "type": raw.get("type", "unknown"),
        "badge_id": raw.get("badgeId"),
        "required_trophies": raw.get("requiredTrophies", 0),
        "trophies": raw.get("trophies", 0),
        "members": members,
        "member_count": len(members),
    }


# Rótulos de cargo do clube (a API devolve camelCase em inglês).
ROLE_LABELS = {
    "president": "Presidente",
    "vicePresident": "Vice-Presidente",
    "senior": "Sênior",
    "member": "Membro",
    "notMember": "Sem clube",
}

# Rótulos de tipo de entrada do clube.
CLUB_TYPE_LABELS = {
    "open": "Aberto",
    "inviteOnly": "Só convite",
    "closed": "Fechado",
}


def role_label(role: str | None) -> str:
    return ROLE_LABELS.get(role or "member", "Membro")


def club_type_label(t: str | None) -> str:
    return CLUB_TYPE_LABELS.get(t or "unknown", "Não informado")


# --------------------------------------------------------------- Rankings ---
def player_rankings(country: str = "global") -> list[dict]:
    """Top de jogadores da região (com cache)."""
    country = country if is_valid_country(country) else "global"
    raw = hub_cache.cached(
        f"rankings:players:{country}",
        hub_cache.TTL_RANKINGS,
        lambda: SupercellClient().rankings("players", country),
    )
    return [normalize_player_ranking(i) for i in raw]


def club_rankings(country: str = "global") -> list[dict]:
    """Top de clubes da região (com cache)."""
    country = country if is_valid_country(country) else "global"
    raw = hub_cache.cached(
        f"rankings:clubs:{country}",
        hub_cache.TTL_RANKINGS,
        lambda: SupercellClient().rankings("clubs", country),
    )
    return [normalize_club_ranking(i) for i in raw]


def brawler_rankings(brawler_id: int, country: str = "global") -> list[dict]:
    """Top de jogadores por um Brawler específico (com cache)."""
    country = country if is_valid_country(country) else "global"
    raw = hub_cache.cached(
        f"rankings:brawlers:{brawler_id}:{country}",
        hub_cache.TTL_RANKINGS,
        lambda: SupercellClient().brawler_rankings(brawler_id, country),
    )
    return [normalize_player_ranking(i) for i in raw]


# ------------------------------------------------------------------ Clube ---
def club_detail(tag: str) -> dict:
    """Um clube completo, com membros (com cache)."""
    raw = hub_cache.cached(
        f"club:{tag}", hub_cache.TTL_RANKINGS, lambda: SupercellClient().club(tag)
    )
    return normalize_club(raw)
