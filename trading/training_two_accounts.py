"""Opérationnel : simuler la RÉALITÉ des deux comptes séparés (leçon 49).
- PEA : ETF monde uniquement, ne reçoit que des versements, ne sort jamais d'argent.
- Kraken : BTC/ETH avec la règle de tendance (zone ±3 %), refuge en stablecoin à l'intérieur du compte.
Rééquilibrage : uniquement par les versements mensuels, envoyés vers le compte sous sa cible (70 / 30).
Comparé au robot actuel (un seul compte, rééquilibrage à 2 points), avec les mêmes versements.
Usage : python3 trading/training_two_accounts.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd

import backtest as bt
import strategies as st
from data import clean_spikes, load_prices
from research import daily

COST = 0.002


def simulate(p: pd.DataFrame, start: float, monthly: float, separate: bool, band: float = 0.02) -> tuple[pd.Series, pd.Series, float]:
    crypto = ["BTC-USD", "ETH-USD"]
    on = (st.trend_band(p[crypto], 150, 0.03) > 0).shift(1).fillna(False)
    u = {"ACWI": 0.0, "BTC-USD": 0.0, "ETH-USD": 0.0}
    cash_pea, cash_kr = start * 0.70, start * 0.30
    invested, eq, wcrypto = start, [], []
    for i, d in enumerate(p.index):
        px = p.loc[d]
        new_month = i > 0 and d.month != p.index[i - 1].month
        if new_month and monthly:
            invested += monthly
            pea = cash_pea + u["ACWI"] * px["ACWI"]
            kr = cash_kr + u["BTC-USD"] * px["BTC-USD"] + u["ETH-USD"] * px["ETH-USD"]
            if separate:                                   # le versement va au compte sous sa cible
                if pea / (pea + kr + monthly) < 0.70:
                    cash_pea += monthly
                else:
                    cash_kr += monthly
            else:
                cash_pea += monthly
        # PEA : tout le cash est investi en ETF (achat seulement)
        if cash_pea > 1e-9:
            u["ACWI"] += cash_pea * (1 - COST) / px["ACWI"]
            cash_pea = 0.0
        # Kraken (ou partie crypto du compte unique)
        if separate:
            kr = cash_kr + sum(u[c] * px[c] for c in crypto)
            for c in crypto:
                tgt = kr / 2 if on.loc[d, c] else 0.0
                cur = u[c] * px[c]
                if (tgt == 0 and u[c] > 0) or (tgt > 0 and abs(tgt - cur) / max(kr, 1e-9) > 0.10) or (tgt > 0 and u[c] == 0):
                    diff = tgt - cur
                    if diff > 0:
                        diff = min(diff, cash_kr / (1 + COST))
                    u[c] = 0.0 if tgt == 0 else u[c] + diff / px[c]
                    cash_kr -= diff + abs(diff) * COST
        else:                                              # compte unique : rééquilibrage 70/30 complet au seuil
            tot = cash_kr + sum(u[a] * px[a] for a in u)
            tgts = {"ACWI": 0.70, "BTC-USD": 0.15 * on.loc[d, "BTC-USD"], "ETH-USD": 0.15 * on.loc[d, "ETH-USD"]}
            for a in sorted(u, key=lambda a: tgts[a] * tot - u[a] * px[a]):   # ventes d'abord
                cur = u[a] * px[a]
                tgt = tgts[a] * tot
                if abs(tgt - cur) / tot > band or (tgt == 0 and u[a] > 0):
                    diff = tgt - cur
                    if diff > 0:
                        diff = min(diff, cash_kr / (1 + COST))
                    u[a] = 0.0 if tgt == 0 else u[a] + diff / px[a]
                    cash_kr -= diff + abs(diff) * COST
        total = cash_pea + cash_kr + sum(u[a] * px[a] for a in u)
        eq.append(total)
        wcrypto.append((cash_kr + sum(u[c] * px[c] for c in crypto)) / total if separate else
                       (sum(u[c] * px[c] for c in crypto) + cash_kr) / total)
    return pd.Series(eq, index=p.index), pd.Series(wcrypto, index=p.index), invested


def main():
    raw, _ = clean_spikes(load_prices(["ACWI", "BTC-USD", "ETH-USD"], start="2014-01-01"))
    p = daily(raw).loc["2017-11-09":].dropna()
    p = p.iloc[150:]
    full = daily(raw).loc["2017-11-09":].dropna()
    md = ["# Deux comptes séparés (réalité) contre un compte unique (robot actuel)", "",
          f"{full.index[0].date()} → {p.index[-1].date()} (crypto en stablecoin les 150 premiers jours, le temps de calculer la moyenne), 10 000 au départ, frais 0,20 %. Perte max affichée depuis le {p.index[0].date()}.", "",
          "| Scénario | Versement mensuel | Total versé | Capital final | Perte max | Part crypto + stablecoin : min / max / fin |",
          "|---|---|---|---|---|---|"]
    for monthly in (0, 100, 300):
        for name, sep in (("Compte unique (robot actuel)", False), ("Deux comptes, rééquilibrage par versements", True)):
            eq, wc, inv = simulate(full, 10_000, monthly, sep)
            eq, wc = eq.loc[p.index], wc.loc[p.index]
            # perte max sur la valeur par part (neutralise les versements)
            flows = eq.diff().fillna(0)
            dd = bt.metrics(eq / eq.iloc[0])["perte_max"] if monthly == 0 else float("nan")
            md.append(f"| {name} | {monthly} | {inv:,.0f} | {eq.iloc[-1]:,.0f} | {dd:.0%} | {wc.min():.0%} / {wc.max():.0%} / {wc.iloc[-1]:.0%} |"
                      .replace("nan%", "—"))
    out = "\n".join(md) + "\n"
    (Path(__file__).parent / "training_two_accounts_results.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
