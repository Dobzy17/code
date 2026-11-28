"""Hors marché : l'activité réelle du réseau Bitcoin (transactions par jour, puissance de calcul) annonce-t-elle le prix ?
Donnée du jour J utilisée à partir de J+1. Signal : variation sur 30 jours de l'activité, classée en 5 groupes ;
on regarde le rendement de BTC les 30 et 90 jours suivants dans chaque groupe (2016 → aujourd'hui).
Usage : python3 trading/training_onchain.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd
import requests

from data import load_prices
from research import daily


def chart(name: str) -> pd.Series:
    js = requests.get(f"https://api.blockchain.info/charts/{name}", params={"timespan": "all", "format": "json", "sampled": "false"},
                      timeout=120).json()["values"]
    s = pd.Series({pd.to_datetime(v["x"], unit="s").normalize(): v["y"] for v in js}).sort_index()
    return s[~s.index.duplicated()]


def main():
    btc = daily(load_prices(["BTC-USD"], start="2014-01-01"))["BTC-USD"]
    md = ["# Activité de la blockchain Bitcoin et prix", "",
          "| Indicateur | Groupe (variation sur 30 j de l'indicateur) | Jours | BTC +30 j (médiane) | BTC +90 j (médiane) |",
          "|---|---|---|---|---|"]
    for name, lab in (("n-transactions", "Transactions par jour"), ("hash-rate", "Puissance de calcul")):
        s = chart(name).reindex(btc.index).ffill().shift(1)        # connu le lendemain
        s = s.rolling(7).mean()                                    # lisse le bruit quotidien
        chg = (s / s.shift(30) - 1)["2016-01-01":]
        f30 = (btc.shift(-30) / btc - 1).reindex(chg.index)
        f90 = (btc.shift(-90) / btc - 1).reindex(chg.index)
        q = pd.qcut(chg, 5, labels=["1 (forte baisse)", "2", "3", "4", "5 (forte hausse)"])
        for g in q.cat.categories:
            m = q == g
            md.append(f"| {lab} | {g} | {int(m.sum())} | {f30[m].median():+.1%} | {f90[m].median():+.1%} |")
        spread = f90[q == q.cat.categories[-1]].median() - f90[q == q.cat.categories[0]].median()
        for a, b in (("2016", "2020"), ("2021", "2026")):
            qq = q[a:b]
            ff = f90[a:b]
            sp = ff[qq == q.cat.categories[-1]].median() - ff[qq == q.cat.categories[0]].median()
            md.append(f"| {lab} | écart groupe 5 − groupe 1 à 90 j, {a}-{b} | | | {sp:+.1%} |")
        md.append(f"| {lab} | **aujourd'hui : variation sur 30 j {chg.iloc[-1]:+.0%}** | | | |")
    out = "\n".join(md) + "\n"
    (Path(__file__).parent / "training_onchain_results.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
