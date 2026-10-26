"""Tags de template do app players."""
from django import template

register = template.Library()


@register.simple_tag
def power_levels(brawlers):
    """
    Devolve os níveis de poder distintos presentes na lista, ordenados.
    Usado para popular o filtro 'nível de poder' sem consultar a API.
    """
    levels = {b.get("power") for b in brawlers if b.get("power")}
    return sorted(levels)
