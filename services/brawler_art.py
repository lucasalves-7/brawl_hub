"""
Geração de avatares originais para Brawlers.

A API da Supercell devolve apenas IDs e nomes — NÃO fornece URLs de imagem.
Para manter o Brawl Hub com identidade própria (e não depender de artes da
Supercell), cada Brawler recebe um avatar original gerado aqui: um ladrilho
com monograma e uma cor derivada de forma determinística do seu nome.

Assim, qualquer um dos 100+ Brawlers ganha um retrato consistente e próprio.
"""
from __future__ import annotations

import re
from urllib.parse import quote

_GLYPH_FONT = "Lilita One, 'Arial Black', sans-serif"


def initials(name: str | None) -> str:
    """Ex.: 'SHELLY' -> 'SH', 'MR. P' -> 'MP', '8-BIT' -> '8B'."""
    parts = [p for p in re.split(r"[^A-Za-z0-9]+", (name or "").upper()) if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2]
    return parts[0][0] + parts[1][0]


def _hue(name: str) -> int:
    """Cor estável por nome (mesmo Brawler => sempre a mesma cor)."""
    return sum(ord(c) for c in name.upper()) % 360


def brawler_avatar(name: str | None, _brawler_id: int | None = None) -> str:
    """Devolve um data URI SVG original para o Brawler."""
    safe_name = (name or "?").upper()
    hue = _hue(safe_name)
    c1 = f"hsl({hue},72%,58%)"
    c2 = f"hsl({(hue + 38) % 360},70%,38%)"
    ini = initials(safe_name)
    font_size = 92 if len(ini) <= 2 else 70

    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">'
        '<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/>'
        "</linearGradient></defs>"
        '<rect width="200" height="200" rx="26" fill="url(#g)"/>'
        # Estrela decorativa ao fundo
        '<path d="M100 22 L113 62 L155 62 L121 87 L134 128 L100 103 L66 128 '
        'L79 87 L45 62 L87 62 Z" fill="#ffffff" opacity="0.13"/>'
        # Monograma com contorno
        f'<text x="100" y="127" font-family="{_GLYPH_FONT}" font-size="{font_size}" '
        'text-anchor="middle" fill="#ffffff" stroke="#101a33" stroke-width="9" '
        f'paint-order="stroke" letter-spacing="2">{ini}</text>'
        '<rect x="4" y="4" width="192" height="192" rx="22" fill="none" '
        'stroke="rgba(0,0,0,0.32)" stroke-width="8"/>'
        "</svg>"
    )
    return "data:image/svg+xml," + quote(svg, safe="")


# ---------------------------------------------------------------------------
# Imagens REAIS dos Brawlers.
#
# A API da Supercell não devolve URLs de imagem — só IDs. Usamos o CDN público
# do Brawlify (assets extraídos do jogo / Fan Kit oficial), que é feito para ser
# linkado por ID. Se alguma imagem falhar (brawler novo ainda sem asset), o
# avatar gerado acima entra como fallback no front-end.
# ---------------------------------------------------------------------------
BRAWLIFY_CDN = "https://cdn.brawlify.com"


def brawler_image(brawler_id: int | None) -> str | None:
    """Retrato limpo do Brawler (sem moldura, preenche o tile)."""
    if not brawler_id:
        return None
    return f"{BRAWLIFY_CDN}/brawlers/borderless/{brawler_id}.png"


def player_icon_image(icon_id: int | None) -> str | None:
    """Ícone de perfil real escolhido pelo jogador."""
    if not icon_id:
        return None
    return f"{BRAWLIFY_CDN}/profile-icons/regular/{icon_id}.png"


# ---------------------------------------------------------------------------
# Imagens do catálogo global (Fase 5) — mesmas fontes/variantes do CDN.
# A API devolve só IDs; o CDN tem ícones reais para cada acessório.
# ---------------------------------------------------------------------------
def brawler_model_image(brawler_id: int | None) -> str | None:
    """Retrato de corpo inteiro do Brawler (herói da ficha)."""
    if not brawler_id:
        return None
    return f"{BRAWLIFY_CDN}/brawlers/model/{brawler_id}.png"


def brawler_portrait_image(brawler_id: int | None) -> str | None:
    """Retrato largo (paisagem) do Brawler."""
    if not brawler_id:
        return None
    return f"{BRAWLIFY_CDN}/brawlers/portraits/{brawler_id}.png"


def star_power_image(star_power_id: int | None) -> str | None:
    if not star_power_id:
        return None
    return f"{BRAWLIFY_CDN}/star-powers/regular/{star_power_id}.png"


def gadget_image(gadget_id: int | None) -> str | None:
    if not gadget_id:
        return None
    return f"{BRAWLIFY_CDN}/gadgets/regular/{gadget_id}.png"


def gear_image(gear_id: int | None) -> str | None:
    if not gear_id:
        return None
    return f"{BRAWLIFY_CDN}/gears/regular/{gear_id}.png"
