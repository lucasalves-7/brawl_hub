"""
Cliente da API oficial da Supercell (Brawl Stars).

Responsabilidades:
- Montar a requisição com autenticação Bearer e timeout.
- Normalizar e codificar a tag do jogador (`#` vira `%23` na URL).
- Traduzir falhas HTTP/rede em erros claros para a interface.

A chave da API vem de settings.SUPERCELL_API_KEY (lida do .env) e nunca é
exposta no HTML nem no JavaScript enviado ao navegador.
"""
from __future__ import annotations

from urllib.parse import quote

import requests
from django.conf import settings

# Conjunto de caracteres aceito em tags de Brawl Stars.
_TAG_CHARS = set("0289PYLQGRJCUV")


class SupercellAPIError(Exception):
    """Erro controlado da API, com status e mensagem amigável."""

    def __init__(self, status: int | None, message: str):
        self.status = status
        self.message = message
        super().__init__(message)


def normalize_tag(tag: str | None) -> str:
    """Garante que a tag comece com `#` e esteja em maiúsculas."""
    t = (tag or "").strip().upper()
    if not t.startswith("#"):
        t = "#" + t
    return t


def is_valid_tag(tag: str | None) -> bool:
    """Valida o formato de uma tag sem consultar a API."""
    body = normalize_tag(tag)[1:]
    if not (3 <= len(body) <= 14):
        return False
    return all(ch in _TAG_CHARS for ch in body)


def encode_tag(tag: str) -> str:
    """Codifica a tag para uso em URL (`#` -> `%23`)."""
    return quote(normalize_tag(tag), safe="")


class SupercellClient:
    """Cliente leve e sem estado para os endpoints da Brawl Stars API."""

    def __init__(self, base_url: str | None = None, api_key: str | None = None,
                 timeout: int | None = None):
        self.base_url = (base_url or settings.SUPERCELL_API_BASE).rstrip("/")
        self.api_key = settings.SUPERCELL_API_KEY if api_key is None else api_key
        self.timeout = timeout or settings.SUPERCELL_REQUEST_TIMEOUT
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json",
            }
        )

    # ---------------------------------------------------------- Núcleo ----
    def _get(self, path: str, params: dict | None = None):
        if not self.api_key:
            raise SupercellAPIError(
                None, "Chave da API não configurada. Defina SUPERCELL_API_KEY no .env."
            )

        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            resp = self._session.get(url, params=params, timeout=self.timeout)
        except requests.Timeout:
            raise SupercellAPIError(408, "A Supercell demorou para responder. Tente de novo.")
        except requests.RequestException:
            raise SupercellAPIError(None, "Não foi possível falar com a Supercell agora.")

        if resp.status_code == 200:
            try:
                return resp.json()
            except ValueError:
                raise SupercellAPIError(None, "A Supercell retornou uma resposta inválida.")

        if resp.status_code == 404:
            raise SupercellAPIError(404, "Tag não encontrada. Confira e tente novamente.")
        if resp.status_code == 403:
            raise SupercellAPIError(403, "Chave da API inválida ou sem permissão.")
        if resp.status_code == 429:
            raise SupercellAPIError(429, "Muitas consultas. Aguarde um instante e tente de novo.")

        raise SupercellAPIError(resp.status_code, f"A API retornou o erro {resp.status_code}.")

    # ------------------------------------------------------- Endpoints ----
    def player(self, tag: str) -> dict:
        """Perfil completo do jogador, incluindo a lista de Brawlers."""
        return self._get(f"players/{encode_tag(tag)}")

    def battlelog(self, tag: str) -> list[dict]:
        """Histórico de partidas recentes disponível para o jogador."""
        data = self._get(f"players/{encode_tag(tag)}/battlelog")
        return data.get("items", []) if isinstance(data, dict) else []

    def club(self, tag: str) -> dict:
        return self._get(f"clubs/{encode_tag(tag)}")

    def club_members(self, tag: str) -> list[dict]:
        data = self._get(f"clubs/{encode_tag(tag)}/members")
        return data.get("items", []) if isinstance(data, dict) else []

    def brawlers_catalog(self, limit: int = 50, after: str | None = None) -> dict:
        params = {"limit": limit}
        if after:
            params["after"] = after
        return self._get("brawlers", params=params)

    def event_rotation(self, limit: int = 50) -> list[dict]:
        data = self._get("events/rotation", params={"limit": limit})
        return data if isinstance(data, list) else []

    def rankings(self, kind: str = "players", country: str = "global") -> list[dict]:
        """Rankings oficiais. `kind` em {players, clubs}."""
        data = self._get(f"rankings/{country}/{kind}")
        return data.get("items", []) if isinstance(data, dict) else []

    def brawler_rankings(
        self, brawler_id: int, country: str = "global"
    ) -> list[dict]:
        """
        Top de jogadores por um Brawler específico.

        Obs.: a lista de Brawlers (`/rankings/.../brawlers`) NÃO existe (404);
        só há o ranking de jogadores DADO um id de Brawler.
        """
        data = self._get(f"rankings/{country}/brawlers/{brawler_id}")
        return data.get("items", []) if isinstance(data, dict) else []
