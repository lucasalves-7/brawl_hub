"""Raridades catalogadas dos Brawlers atuais.

A API oficial não devolve raridade. Esta tabela é uma camada de apresentação
separada, baseada no catálogo da comunidade, sem alterar o payload da API.
"""
from __future__ import annotations

_GROUPS = {
    "Lendário": "Amber Chester Cordelius Crow Draco Kenji Kit Leon Meg Nori Pierce Sandy Spike Surge",
    "Mítico": "Alli Buster Buzz Byron Charlie Chuck Clancy Cosmo Damian Doug Eve Fang Finx Gene Gigi Glowy Gray Janet Juju Lily Lou Lumi Max Melodie Mico Mina Moe Mortis Mr._P Najia Ollie Otis R-T Ruffs Sprout Squeak Starr_Nova Tara Vince Wendy Willow Ziggy",
    "Épico": "Angelo Ash Bea Belle Berry Bibi Bo Bonnie Colette Edgar Emz Frank Gale Griff Grom Hank Larry_&_Lawrie Lola Maisie Mandy Meeple Nani Pam Pearl Piper Sam Shade Stu Trunk",
    "Super-raro": "8-Bit Carl Darryl Dynamike Gus Jacky Jessie Penny Rico Tick",
    "Raro": "Barley Brock Bull Colt El_Primo Nita Poco Rosa",
    "Ultra": "Kaze Sirius",
    "Inicial": "Shelly",
}

RARITY_BY_NAME: dict[str, str] = {}
for _label, _names in _GROUPS.items():
    for _name in _names.split():
        RARITY_BY_NAME[_name.replace("_", " ")] = _label

# Nomes compostos que usam espaços e símbolos não podem ser separados pelo
# agrupamento compacto acima.
RARITY_BY_NAME["Larry & Lawrie"] = "Épico"
RARITY_BY_NAME["Mr. P"] = "Mítico"
RARITY_BY_NAME["El Primo"] = "Raro"
RARITY_BY_NAME["Starr Nova"] = "Mítico"


def rarity_for(name: str) -> str:
    return RARITY_BY_NAME.get(name, "Não informada")
