"""Rótulos em português para os nomes do kit devolvidos pela API."""
from __future__ import annotations

import re


# A API oficial devolve os nomes do kit em inglês. Estes são os nomes
# localizados usados pela interface; o nome bruto continua preservado no
# payload para não alterar dados da Supercell.
EXACT = {
    "SHELL SHOCK": "Choque de Cartuchos",
    "BAND-AID": "Curativo",
    "FAST FORWARD": "Avanço Rápido",
    "CLAY PIGEONS": "Pombos de Argila",
    "SPEED": "Velocidade",
    "HEALTH": "Vida",
    "DAMAGE": "Dano",
    "VISION": "Visão",
    "SHIELD": "Escudo",
    "GADGET COOLDOWN": "Recarga de Acessório",
    "RELOAD SPEED": "Velocidade de Recarga",
    "DOUBLE BARREL": "Canos Duplos",
    "STAR POWER": "Poder de Estrela",
}

WORDS = {
    "HEALTH": "Vida", "DAMAGE": "Dano", "SPEED": "Velocidade",
    "SHIELD": "Escudo", "VISION": "Visão", "POWER": "Poder",
    "RELOAD": "Recarga", "ATTACK": "Ataque", "SUPER": "Super",
    "FAST": "Rápido", "SLOW": "Lento", "SLOWING": "Lentidão",
    "HEALING": "Cura", "HEAL": "Curar", "BOOSTER": "Impulsionador",
    "BOOST": "Impulso", "SHOT": "Disparo", "SHOTS": "Disparos",
    "BULLET": "Projétil", "BULLETS": "Projéteis", "RANGE": "Alcance",
    "FIELD": "Campo", "FORCE": "Força", "STORM": "Tempestade",
    "FIRE": "Fogo", "FLAME": "Chama", "FLAMES": "Chamas",
    "ICE": "Gelo", "COLD": "Frio", "HOT": "Quente", "DARKNESS": "Escuridão",
    "STAR": "Estrela", "STARS": "Estrelas", "NIGHT": "Noite",
    "BEAR": "Urso", "BOMB": "Bomba", "ROCKET": "Foguete",
    "GADGET": "Gadget", "COOLDOWN": "Recarga", "DASH": "Avanço",
    "JUMP": "Salto", "HIT": "Acerto", "KICK": "Chute", "PUNCH": "Soco",
    "TURRET": "Torreta", "TRAP": "Armadilha", "WALL": "Parede",
    "SHADOW": "Sombra", "POISON": "Veneno", "TOXIC": "Tóxico",
    "BLADE": "Lâmina", "BUSH": "Moita", "BUSHES": "Moitas",
    "HIDDEN": "Oculto", "INVISIBLE": "Invisível", "SPEEDING": "Acelerado",
}


def translate_kit_name(name: str) -> str:
    """Traduz o nome conhecido e aplica fallback palavra a palavra."""
    raw = (name or "").strip()
    if not raw:
        return raw
    exact = EXACT.get(raw.upper())
    if exact:
        return exact

    def replace(match):
        word = match.group(0)
        return WORDS.get(word.upper(), word)

    return re.sub(r"[A-Za-z]+", replace, raw)
