"""
Cache de consultas à Supercell.

Regra do plano (seção 9.4): não consultar a API a cada interação. Os resultados
são guardados por um tempo curto, variável conforme o tipo de dado:

- perfil e battlelog: mudam devagar  -> TTL menor, atualiza com frequência
- rotação de eventos: muda por dia    -> TTL médio
- rankings: mudam por temporada      -> TTL maior

O backend é o LocMemCache configurado em settings.CACHES.
"""
from __future__ import annotations

from django.core.cache import cache

# Tempos de vida (em segundos) por tipo de dado.
TTL_PLAYER = 5 * 60        # 5 min
TTL_BATTLELOG = 5 * 60     # 5 min
TTL_RANKINGS = 60 * 60     # 1 h
TTL_EVENTS = 30 * 60       # 30 min
TTL_STATIC = 24 * 60 * 60  # 24 h


def cached(key: str, ttl: int, fetcher):
    """
    Devolve o valor em cache; se não houver, chama `fetcher`, guarda e devolve.

    Se `fetcher` lançar exceção, ela é propagada e nada é cacheado — assim uma
    falha temporária não fica "grudada" no cache.
    """
    hit = cache.get(key)
    if hit is not None:
        return hit
    value = fetcher()
    cache.set(key, value, ttl)
    return value


def invalidate(prefix: str | None = None) -> None:
    """Limpa o cache todo (ou só as chaves com o prefixo, quando suportado)."""
    if prefix is None:
        cache.clear()
