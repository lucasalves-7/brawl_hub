"""
Camada de estatísticas do Brawl Hub.

Separa com clareza o que é dado oficial do que é calculado aqui (plano, seção 10):

- Grupo A (fornecido): troféus, vitórias acumuladas, lista de Brawlers etc.
  -> repassados como retornados pela API.
- Grupo B (calculado): quantidade de Brawlers, distribuição de troféus,
  aproveitamento da amostra etc. -> calculados aqui e SEMPRE rotulados.
"""
from __future__ import annotations

from collections import Counter, defaultdict

# Rótulos legíveis para os modos de jogo, em português (a API devolve
# camelCase em inglês).
MODE_LABELS = {
    "gemGrab": "Mina de Gemas",
    "brawlBall": "Bola no Pé",
    "bounty": "Guerra de Estrelas",
    "heist": "Cofre",
    "knockout": "Nocaute",
    "hotZone": "Zona Quente",
    "duel": "Duelo",
    "payload": "Escolta",
    "wipeout": "Aniquilação",
    "brawlBall5V5": "Bola no Pé 5v5",
    "gemGrab3V3": "Mina de Gemas 3v3",
    "soloShowdown": "Combate Solo",
    "duoShowdown": "Combate Dupla",
    "roboRumble": "Robô Rumble",
    "bigGame": "Caça ao Monstro",
    "bossFight": "Luta contra o Chefe",
    "communityGames": "Jogos da Comunidade",
    "ranked": "Ranqueada",
    "friendly": "Amistoso",
    "clubLeague": "Liga do Clube",
    "clubQuest": "Missões do Clube",
}


def mode_label(mode: str | None) -> str:
    if not mode:
        return "Modo desconhecido"
    return MODE_LABELS.get(mode, mode.replace("_", " ").title())


# --------------------------------------------------------------- Grupo A ---
def normalize_player(raw: dict) -> dict:
    """Reduz o payload da API aos campos que a interface realmente usa."""
    club = raw.get("club") or {}
    return {
        "tag": raw.get("tag", ""),
        "name": raw.get("name", ""),
        "name_color": raw.get("nameColor"),
        "trophies": raw.get("trophies", 0),
        "highest_trophies": raw.get("highestTrophies", 0),
        "exp_level": raw.get("expLevel", 0),
        "exp_points": raw.get("expPoints", 0),
        "fame": raw.get("fame", 0),
        "fame_tier_name": raw.get("fameTierName"),
        "victories_3vs3": raw.get("3vs3Victories", 0),
        "solo_victories": raw.get("soloVictories", 0),
        "duo_victories": raw.get("duoVictories", 0),
        "best_robo_rumble": raw.get("bestRoboRumbleTime", 0),
        "ranked_rank": raw.get("rankedRank"),
        "ranked_rank_name": raw.get("rankedRankName"),
        "ranked_elo": raw.get("rankedElo"),
        "highest_rank_name": raw.get("highestAllTimeRankedRankName"),
        "club_tag": club.get("tag"),
        "club_name": club.get("name"),
    }


def normalize_brawler(b: dict) -> dict:
    """Normaliza um Brawler do perfil do jogador."""
    return {
        "id": b.get("id"),
        "name": b.get("name", "").title(),
        "raw_name": b.get("name", ""),
        "power": b.get("power", 0),
        "rank": b.get("rank", 0),
        "trophies": b.get("trophies", 0),
        "highest_trophies": b.get("highestTrophies", 0),
        "win_streak": b.get("currentWinStreak", 0),
        "max_win_streak": b.get("maxWinStreak", 0),
        "has_hypercharge": bool((b.get("buffies") or {}).get("hyperCharge")),
        "gadgets": len(b.get("gadgets") or []),
        "star_powers": len(b.get("starPowers") or []),
        "gears": len(b.get("gears") or []),
    }


# --------------------------------------------------------------- Grupo B ---
def brawler_count(brawlers: list[dict]) -> int:
    """Grupo B: quantidade de Brawlers encontrados no perfil."""
    return len(brawlers)


def trophy_distribution(brawlers: list[dict], top: int = 10) -> list[dict]:
    """
    Grupo B: distribuição dos troféus entre os personagens.
    Devolve os `top` maiores, prontos para o gráfico.
    """
    ordered = sorted(brawlers, key=lambda x: x["trophies"], reverse=True)
    return [
        {"name": b["name"], "trophies": b["trophies"], "power": b["power"]}
        for b in ordered[:top]
    ]


def _classify(battle: dict, player_tag: str) -> tuple[str, dict | None]:
    """
    Classifica uma batalha como 'win' / 'loss' / 'draw' / 'unknown' e devolve
    a entrada do próprio jogador na partida (quando encontrada).
    """
    player_entry = None

    # Times (modos em equipe / ranqueada)
    for team in battle.get("teams") or []:
        for p in team:
            if p.get("tag") == player_tag:
                player_entry = p
    # Lista plana (showdown solo/dupla)
    if player_entry is None:
        for p in battle.get("players") or []:
            if p.get("tag") == player_tag:
                player_entry = p

    result = battle.get("result")
    if result == "victory":
        return "win", player_entry
    if result == "defeat":
        return "loss", player_entry
    if result == "draw":
        return "draw", player_entry

    # Sem `result`: showdown usa a posição final (1º = vitória).
    rank = battle.get("rank")
    if rank is not None:
        return ("win" if rank == 1 else "loss"), player_entry

    return "unknown", player_entry


def recent_performance(battlelog: list[dict], player_tag: str) -> dict:
    """
    Grupo B: aproveitamento calculado SOMENTE sobre a amostra disponível.

    Fórmula do plano (seção 4.3):
        aproveitamento = vitórias / partidas válidas * 100
    Partidas sem resultado identificável ficam FORA do denominador.
    """
    wins = losses = draws = uncounted = 0
    trophy_delta = 0
    trophy_delta_count = 0
    by_mode: dict[str, dict] = defaultdict(lambda: {"total": 0, "wins": 0, "losses": 0, "draws": 0})
    brawlers_used: Counter = Counter()
    battles: list[dict] = []

    for item in battlelog:
        battle = item.get("battle") or {}
        event = item.get("event") or {}
        outcome, entry = _classify(battle, player_tag)

        if outcome == "unknown":
            uncounted += 1
            continue

        if outcome == "win":
            wins += 1
        elif outcome == "loss":
            losses += 1
        else:
            draws += 1

        mode = battle.get("mode") or event.get("mode")
        bucket = by_mode[mode]
        bucket["total"] += 1
        bucket[{"win": "wins", "loss": "losses", "draw": "draws"}[outcome]] += 1

        brawler_name = None
        if entry and entry.get("brawler"):
            brawler_name = entry["brawler"].get("name", "").title()
            brawlers_used[brawler_name] += 1

        tc = battle.get("trophyChange")
        if isinstance(tc, int):
            trophy_delta += tc
            trophy_delta_count += 1

        battles.append(
            {
                "battle_time": item.get("battleTime"),
                "mode": mode,
                "mode_label": mode_label(mode),
                "map": event.get("map"),
                "result": outcome,
                "trophy_change": tc,
                "brawler": brawler_name,
                "duration": battle.get("duration"),
                "rank": battle.get("rank"),
            }
        )

    valid = wins + losses + draws
    win_rate = round(wins / valid * 100, 1) if valid else None

    mode_stats = []
    for mode, b in by_mode.items():
        m_valid = b["wins"] + b["losses"] + b["draws"]
        mode_stats.append(
            {
                "mode": mode,
                "label": mode_label(mode),
                "total": m_valid,
                "wins": b["wins"],
                "losses": b["losses"],
                "draws": b["draws"],
                "win_rate": round(b["wins"] / m_valid * 100, 1) if m_valid else None,
            }
        )
    mode_stats.sort(key=lambda x: x["total"], reverse=True)

    return {
        "sample_size": len(battlelog),
        "valid": valid,
        "wins": wins,
        "losses": losses,
        "draws": draws,
        "uncounted": uncounted,
        "win_rate": win_rate,
        "trophy_delta": trophy_delta if trophy_delta_count else None,
        "brawlers_used": [
            {"name": name, "count": count}
            for name, count in brawlers_used.most_common(8)
        ],
        "by_mode": mode_stats,
        "battles": battles,
    }
