"""Garde-fous du module argent réel. Fonctions pures, testées : aucune ne dépend du réseau.

Chaque garde-fou renvoie une liste de raisons de BLOQUER. Liste vide = feu vert.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

import pandas as pd


@dataclass(frozen=True)
class Limits:
    max_order_eur: float = 250.0         # aucun ordre au-delà, quoi qu'il arrive (pilote de 500 €, 18/11/2026)
    max_daily_eur: float = 500.0         # total des ordres d'une journée
    max_data_age_h: float = 48.0         # données plus vieilles : on ne fait rien
    max_daily_move: float = 0.40         # cours qui bouge de plus de 40 % en un jour : donnée suspecte
    kill_drawdown: float = -0.35         # recul depuis le plus haut : arrêt total


def check_data(closes: pd.Series, now: datetime, lim: Limits) -> list[str]:
    reasons = []
    if closes.empty:
        return ["aucune donnée de cours"]
    age = now - closes.index[-1].to_pydatetime() - timedelta(days=1)  # bougie du jour J finit à J+1 00:00 UTC
    if age > timedelta(hours=lim.max_data_age_h):
        reasons.append(f"données trop anciennes ({age.total_seconds() / 3600:.0f} h)")
    move = closes.pct_change().iloc[-1]
    if abs(move) > lim.max_daily_move:
        reasons.append(f"mouvement suspect de {move:+.0%} sur la dernière bougie")
    if len(closes) < 151:
        reasons.append("historique insuffisant pour la moyenne 150 j")
    return reasons


def check_account(equity: float, peak: float, halted: bool, lim: Limits) -> list[str]:
    reasons = []
    if halted:
        reasons.append("coupe-circuit déjà actif : relance humaine requise")
    if peak > 0 and equity / peak - 1 <= lim.kill_drawdown:
        reasons.append(f"recul de {equity / peak - 1:.0%} depuis le plus haut : coupe-circuit")
    return reasons


def cap_orders(orders: list[dict], lim: Limits) -> tuple[list[dict], list[str]]:
    """Plafonne chaque ordre et le total du jour. Renvoie les ordres retenus et les avertissements."""
    kept, notes, total = [], [], 0.0
    for o in orders:
        amt = abs(o["montant_eur"])
        if amt > lim.max_order_eur:
            notes.append(f"{o['actif']} : ordre de {amt:.0f} € réduit à {lim.max_order_eur:.0f} € (plafond par ordre)")
            amt = lim.max_order_eur
        if total + amt > lim.max_daily_eur:
            amt = max(lim.max_daily_eur - total, 0.0)
            notes.append(f"{o['actif']} : plafond journalier atteint, ordre réduit à {amt:.0f} €")
        if amt >= 10:  # en dessous, les frais minimums mangent tout
            kept.append({**o, "montant_eur": amt if o["montant_eur"] > 0 else -amt})
            total += amt
    return kept, notes
