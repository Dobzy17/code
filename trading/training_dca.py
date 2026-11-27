"""Bourse : placer une somme d'un coup, ou l'étaler sur 6 ou 12 mois (DCA) en laissant l'attente en cash rémunéré ?
Pour chaque mois de départ depuis 1976 : valeur 12 mois et 5 ans après le départ. S&P 500 dividendes réinvestis (voir training_curve).
Usage : python3 trading/training_dca.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd

from data import load_prices
from training_curve import equity_returns


def main():
    r = equity_returns()
    idx = (1 + r).cumprod().resample("ME").last()
    rf = (load_prices(["^IRX"], start="1976-01-01")["^IRX"].resample("ME").mean().reindex(idx.index).ffill() / 100 / 12).fillna(0)
    md = ["# D'un coup ou étalé (DCA) ? S&P 500, chaque mois de départ depuis 1976", "",
          "| Étalement | Horizon | Départs testés | Le « d'un coup » gagne | Écart médian (d'un coup − étalé) | Pire cas pour « d'un coup » |",
          "|---|---|---|---|---|---|"]
    for months in (6, 12):
        for horizon in (12, 60):
            res = []
            for i in range(len(idx) - horizon):
                end = i + horizon
                lump = idx.iloc[end] / idx.iloc[i]
                dca, cash = 0.0, 1.0
                part = 1.0 / months
                units = 0.0
                for k in range(months):
                    j = i + k
                    if k > 0:
                        cash *= 1 + rf.iloc[j]
                    units += part / idx.iloc[j]
                    cash -= part
                dca = units * idx.iloc[end] + max(cash, 0)
                res.append((idx.index[i], lump - dca, lump / dca - 1))
            d = pd.DataFrame(res, columns=["date", "diff", "rel"]).set_index("date")
            md.append(f"| {months} mois | {horizon // 12} an(s) | {len(d)} | **{(d['diff'] > 0).mean():.0%}** | "
                      f"{d['rel'].median():+.1%} | {d['rel'].min():+.0%} (départ {d['rel'].idxmin().date()}) |")
    out = "\n".join(md) + "\n"
    (Path(__file__).parent / "training_dca_results.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
