"""Descrições dos Brawlers em português.

A API oficial não fornece biografias. A wiki da comunidade mantém uma versão
pt-BR acessível pela API MediaWiki; o resultado é cacheado por 30 dias para
que uma visita não dependa de consultas repetidas à wiki.
"""
from __future__ import annotations

import html
import re
from urllib.parse import quote
from urllib.request import Request, urlopen

from services import cache as hub_cache


def _intro(name: str) -> str:
    url = (
        "https://brawlstars.fandom.com/pt-br/api.php?action=parse&page="
        f"{quote(name.replace(' ', '_'))}&prop=text&format=json&disabletoc=1"
    )
    request = Request(
        url,
        headers={
            "User-Agent": "BrawlHub/1.0 (projeto independente)",
            "Accept-Language": "pt-BR,pt;q=0.9",
        },
    )
    with urlopen(request, timeout=8) as response:
        import json
        payload = json.loads(response.read().decode("utf-8"))
    source = payload.get("parse", {}).get("text", {}).get("*", "")
    paragraphs = re.findall(r"<p>(.*?)</p>", source, flags=re.S)
    for paragraph in paragraphs:
        text = html.unescape(re.sub(r"<[^>]+>", "", paragraph))
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) >= 60:
            return text
    return ""


def description_for(brawler: dict) -> dict:
    """Anexa uma descrição pt-BR sem deixar a ficha falhar se a wiki cair."""
    name = brawler.get("name", "Brawler")
    key = f"brawler:description:pt:{name.lower()}"
    try:
        description = hub_cache.cached(key, 30 * 24 * 60 * 60, lambda: _intro(name))
    except Exception:
        description = ""

    # Alguns Brawlers recém-lançados ainda não têm artigo pt-BR. Mantemos a
    # interface integralmente em português, sem exibir o texto inglês como
    # fallback, e informamos claramente a limitação da fonte.
    brawler["description"] = description or (
        f"{name} é um Brawler do universo de Brawl Stars. "
        "A descrição detalhada em português ainda não está disponível."
    )
    brawler["description_source"] = "Wiki da comunidade"
    return brawler
