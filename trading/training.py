"""Entraînement : soumettre les stratégies aux tests qui cassent les fausses bonnes idées.

Usage : python3 trading/training.py  → écrit training_results.md
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
import pandas as pd

import backtest as bt
import strategies as st
from data import load_prices
from research import daily

UNIVERSE = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD", "ADA-USD", "DOGE-USD",
            "LTC-USD", "LINK-USD", "AVAX-USD", "DOT-USD", "TRX-USD", "BCH-USD", "XLM-USD"]
CORE2 = ["BTC-USD", "ETH-USD"]
rng = np.random.default_rng(42)


def candidates(p2: pd.DataFrame, pu: pd.DataFrame) -> dict:
    return {
        "A. Achat-conservation BTC+ETH": (p2, st.buy_hold(p2)),
        "B. Robot actuel : SMA150 BTC+ETH": (p2, st.trend_sma(p2, 150)),
        "C. Donchian ensemble BTC+ETH": (p2, st.donchian_ensemble(p2)),
        "D. Donchian + volatilité cible BTC+ETH": (p2, st.vol_target(st.donchian_ensemble(p2), p2)),
        "E. Donchian + vol. cible, 14 cryptos": (pu, st.vol_target(st.donchian_ensemble(pu), pu)),
    }


def bootstrap(eq: pd.Series, n: int = 2000, horizon: int = 365, block: int = 30) -> dict:
    """Rejoue 2000 « années possibles » en recollant des blocs de 30 jours du passé."""
    r = eq.pct_change().dropna().values
    dds, finals = [], []
    for _ in range(n):
        starts = rng.integers(0, len(r) - block, horizon // block + 1)
        path = np.concatenate([r[s:s + block] for s in starts])[:horizon]
        curve = np.cumprod(1 + path)
        dds.append((curve / np.maximum.accumulate(curve) - 1).min())
        finals.append(curve[-1] - 1)
    dds, finals = np.array(dds), np.array(finals)
    return {"proba_perte_1an": (finals < 0).mean(), "rendement_median_1an": np.median(finals),
            "pire_5pct_1an": np.percentile(finals, 5), "perte_max_mediane": np.median(dds),
            "perte_max_pire_5pct": np.percentile(dds, 5)}


def main():
    p2 = daily(load_prices(CORE2, start="2014-01-01")).loc["2018-01-01":].dropna()
    pu = daily(load_prices(UNIVERSE, start="2014-01-01")).loc["2018-01-01":]
    md = ["# Résultats d'entraînement", "",
          f"Données {p2.index[0].date()} → {p2.index[-1].date()}, frais 0,20 % par ordre sauf mention contraire.", ""]

    md += ["## 1. Résultats globaux (avant 2021 = choix / 2021+ = hors échantillon)", "",
           "| Stratégie | Période | Rendement/an | Perte max | Sharpe |", "|---|---|---|---|---|"]
    curves = {}
    for name, (p, w) in candidates(p2, pu).items():
        eq = bt.run(p.fillna(0) if p is pu else p, w.fillna(0))
        curves[name] = eq
        for lab, part in (("avant 2021", eq[:"2020-12-31"]), ("2021+", eq["2021-01-01":])):
            m = bt.metrics(part / part.iloc[0])
            md.append(f"| {name} | {lab} | {m['rendement_annuel']:+.1%} | {m['perte_max']:.1%} | {m['sharpe']:.2f} |")

    md += ["", "## 2. Année par année (régularité)", ""]
    yearly = pd.DataFrame({k: v.resample("YE").last().pct_change().fillna(v.resample("YE").last() - 1)
                           for k, v in curves.items()})
    yearly.index = yearly.index.year
    md += ["| Année | " + " | ".join(k.split(".")[0] for k in curves) + " |",
           "|---" * (len(curves) + 1) + "|"]
    md += [f"| {y} | " + " | ".join(f"{x:+.0%}" for x in row) + " |" for y, row in yearly.iterrows()]

    md += ["", "## 3. Résistance aux frais (rendement/an sur toute la période)", "",
           "| Stratégie | 0,10 % | 0,20 % | 0,50 % | 1,00 % |", "|---|---|---|---|---|"]
    for name, (p, w) in candidates(p2, pu).items():
        pp = p.fillna(0) if p is pu else p
        vals = [bt.metrics(bt.run(pp, w.fillna(0), c))["rendement_annuel"] for c in (10, 20, 50, 100)]
        md.append(f"| {name} | " + " | ".join(f"{v:+.1%}" for v in vals) + " |")

    md += ["", "## 4. Exécution en retard de 2 jours (robot lent, panne…)", "",
           "| Stratégie | À l'heure | +2 jours |", "|---|---|---|"]
    for name, (p, w) in candidates(p2, pu).items():
        pp = p.fillna(0) if p is pu else p
        a = bt.metrics(bt.run(pp, w.fillna(0)))["rendement_annuel"]
        b = bt.metrics(bt.run(pp, w.fillna(0).shift(2).fillna(0)))["rendement_annuel"]
        md.append(f"| {name} | {a:+.1%} | {b:+.1%} |")

    md += ["", "## 5. Simulation de 2 000 années possibles (blocs de 30 jours tirés du passé)", "",
           "| Stratégie | Proba de perdre sur 1 an | Rendement médian | 5 % pires années | Perte max médiane | Perte max (5 % pires) |",
           "|---|---|---|---|---|---|"]
    for name, eq in curves.items():
        b = bootstrap(eq)
        md.append(f"| {name} | {b['proba_perte_1an']:.0%} | {b['rendement_median_1an']:+.0%} | "
                  f"{b['pire_5pct_1an']:+.0%} | {b['perte_max_mediane']:.0%} | {b['perte_max_pire_5pct']:.0%} |")

    md += ["", "_Biais connu : les 14 cryptos sont celles qui existent encore aujourd'hui (biais du survivant) ; "
           "la stratégie E est donc probablement surestimée._"]
    out = "\n".join(md) + "\n"
    Path(__file__).parent.joinpath("training_results.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
