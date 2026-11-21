"""Hors marché : sortir des actions quand la courbe des taux US s'inverse (10 ans − 2 ans < 0) aurait-il protégé ?
Donnée FRED T10Y2Y (quotidienne, depuis 1976), utilisée avec 1 jour de retard (publication).
Actions : S&P 500 (^GSPC + 2,5 %/an de dividendes estimés avant 1993, puis SPY dividendes réinvestis).
Cash : bons du Trésor 3 mois (^IRX). Frais 0,20 % par changement.
Usage : python3 trading/training_curve.py
"""
from __future__ import annotations

import csv
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd
import requests

import backtest as bt
from data import load_prices

P = 252


def fred(series: str) -> pd.Series:
    r = requests.get("https://fred.stlouisfed.org/graph/fredgraph.csv", params={"id": series}, timeout=60)
    r.raise_for_status()
    rows = [x for x in csv.reader(io.StringIO(r.text))][1:]
    return pd.Series({pd.Timestamp(d): float(v) for d, v in rows if v not in (".", "")})


def equity_returns() -> pd.Series:
    gspc = load_prices(["^GSPC"], start="1976-01-01")["^GSPC"].dropna()
    spy = load_prices(["SPY"], start="1993-01-01")["SPY"].dropna()
    r = gspc.pct_change() + 0.025 / P
    r_spy = spy.pct_change()
    r.loc[r_spy.index[1]:] = r_spy.reindex(r.loc[r_spy.index[1]:].index)
    return r.dropna()


def run(r_eq: pd.Series, invested: pd.Series, rf: pd.Series) -> pd.Series:
    inv = invested.reindex(r_eq.index).ffill().fillna(1.0)
    held = inv.shift(1).fillna(1.0)
    cost = held.diff().abs().fillna(0) * 0.002
    rate = rf.reindex(r_eq.index).ffill().fillna(0) / 100 / P
    return (1 + held * r_eq + (1 - held) * rate - cost).cumprod()


def main():
    curve = fred("T10Y2Y").shift(1, freq="D")          # connue le lendemain
    r_eq = equity_returns()
    rf = load_prices(["^IRX"], start="1976-01-01")["^IRX"]
    c = curve.reindex(r_eq.index).ffill()
    inverted = c < 0
    # épisodes d'inversion
    starts = inverted & ~inverted.shift(1, fill_value=False)
    first = [d for d in r_eq.index[starts] if not inverted.loc[d - pd.Timedelta(days=365):d].iloc[:-1].any()]
    level = (1 + r_eq).cumprod()
    md = ["# Courbe des taux inversée : alarme de krach ?", "",
          f"Données {r_eq.index[0].date()} → {r_eq.index[-1].date()}.", "",
          "## 1. Chaque première inversion (après au moins 1 an sans), et la suite pour le S&P 500", "",
          "| Inversion | S&P 500 +6 mois | +12 mois | +24 mois | Pire baisse dans les 24 mois |", "|---|---|---|---|---|"]
    for d in first:
        def fwd(days):
            e = level.loc[d:d + pd.Timedelta(days=days)]
            return e.iloc[-1] / e.iloc[0] - 1 if len(e) > 20 and (e.index[-1] - d).days > days - 10 else float("nan")
        win = level.loc[d:d + pd.Timedelta(days=730)]
        md.append(f"| {d.date()} | {fwd(182):+.0%} | {fwd(365):+.0%} | {fwd(730):+.0%} | {(win / win.cummax() - 1).min():.0%} |")

    md += ["", "## 2. Stratégies (actions ou cash rémunéré)", "",
           "| Stratégie | 1977-1999 | 2000+ | Perte max (tout) | Temps investi |", "|---|---|---|---|---|"]
    strat = {
        "Toujours investi": pd.Series(1.0, index=r_eq.index),
        "Cash pendant l'inversion": (~inverted).astype(float),
    }
    for months in (6, 12, 18):
        out = pd.Series(1.0, index=r_eq.index)
        for d in first:
            out.loc[d:d + pd.DateOffset(months=months)] = 0.0
        strat[f"Cash {months} mois après la 1re inversion"] = out
    for name, inv in strat.items():
        e = run(r_eq, inv, rf)
        a = e["1977-01-01":"1999-12-31"]
        b = e["2000-01-01":]
        ma, mb, mf = bt.metrics(a / a.iloc[0], P), bt.metrics(b / b.iloc[0], P), bt.metrics(e / e.iloc[0], P)
        md.append(f"| {name} | {ma['rendement_annuel']:+.1%} | {mb['rendement_annuel']:+.1%} | {mf['perte_max']:.0%} | {inv.mean():.0%} |")
    md += ["", f"Dernière valeur connue : courbe à {curve.iloc[-1]:+.2f} point (connue le {curve.index[-1].date()})."]
    out = "\n".join(md) + "\n"
    (Path(__file__).parent / "training_curve_results.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
