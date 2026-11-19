"""Hors marché : acheter la « peur extrême » (indice Peur et Avidité crypto) bat-il la règle de tendance ?
Indice publié chaque jour par alternative.me depuis février 2018. Entrée le LENDEMAIN de la publication.
Usage : python3 trading/training_feargreed.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd
import requests

import backtest as bt
import strategies as st
from live.kraken_data import daily_closes  # noqa: F401  (même source que le robot pour la fin de série)
from data import load_prices
from research import daily


def fng() -> pd.Series:
    d = requests.get("https://api.alternative.me/fng/", params={"limit": 0}, timeout=60).json()["data"]
    s = pd.Series({pd.to_datetime(int(x["timestamp"]), unit="s").normalize(): int(x["value"]) for x in d}).sort_index()
    return s


def main():
    f = fng()
    btc = daily(load_prices(["BTC-USD"], start="2017-01-01"))["BTC-USD"].loc[f.index[0]:]
    f = f.reindex(btc.index).ffill()
    md = ["# Peur extrême : signal d'achat ou piège ?", "",
          f"Indice Peur et Avidité de {f.index[0].date()} à {f.index[-1].date()} ({len(f)} jours). "
          "Rendement de BTC après le jour de publication (entrée le lendemain).", "",
          "| Situation | Jours | Après 30 j (médiane) | Après 90 j (médiane) | Après 180 j (médiane) | % de cas positifs à 180 j |",
          "|---|---|---|---|---|---|"]
    entry = btc.shift(-1)
    fwd = {h: btc.shift(-1 - h) / entry - 1 for h in (30, 90, 180)}
    for lab, mask in (("Tous les jours", f.notna()), ("Peur extrême (≤ 15)", f <= 15), ("Peur (16-30)", (f > 15) & (f <= 30)),
                      ("Avidité extrême (≥ 80)", f >= 80)):
        vals = [fwd[h][mask].dropna() for h in (30, 90, 180)]
        md.append(f"| {lab} | {int(mask.sum())} | {vals[0].median():+.0%} | {vals[1].median():+.0%} | {vals[2].median():+.0%} | "
                  f"{(vals[2] > 0).mean():.0%} |")
    # épisodes indépendants : premier jour ≤ 15 après au moins 30 jours sans
    ext = f <= 15
    starts = ext & ~ext.rolling(30, min_periods=1).max().shift(1).fillna(0).astype(bool)
    ep = [(d.date(), fwd[180].get(d)) for d in btc.index[starts]]
    md += ["", f"**Épisodes indépendants de peur extrême** (au moins 30 jours d'écart) : {len(ep)}", "",
           "| Début | BTC 180 j après |", "|---|---|"]
    md += [f"| {d} | {'en cours' if pd.isna(r) else f'{r:+.0%}'} |" for d, r in ep]

    # stratégie : investi 180 j après chaque jour ≤ 15, sinon cash ; contre la règle de tendance du robot
    on = ext.shift(1).fillna(False).astype(float).rolling(180, min_periods=1).max()
    p = btc.to_frame()
    rules = {"BTC sans règle": st.buy_hold(p), "Tendance SMA150 (règle du robot, sans zone)": st.trend_sma(p, 150),
             "Achat 180 j après chaque peur extrême": on.to_frame("BTC-USD"),
             "Tendance OU peur extrême": ((st.trend_sma(p, 150)["BTC-USD"] > 0) | (on > 0)).astype(float).to_frame("BTC-USD")}
    md += ["", "| Stratégie (BTC seul, frais 0,20 %) | Rendement/an | Perte max | Sharpe | Temps investi |", "|---|---|---|---|---|"]
    for name, w in rules.items():
        m = bt.metrics(bt.run(p, w))
        md.append(f"| {name} | {m['rendement_annuel']:+.1%} | {m['perte_max']:.0%} | {m['sharpe']:.2f} | {w.iloc[:, 0].mean():.0%} |")
    out = "\n".join(md) + "\n"
    (Path(__file__).parent / "training_feargreed_results.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
