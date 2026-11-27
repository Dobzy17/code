"""Faut-il garder ETH dans le satellite crypto ? + test glissant (walk-forward) du réglage.

Portefeuille complet testé à chaque fois : 70 % ACWI + 30 % satellite crypto avec tendance.
Usage : python3 trading/training_sleeve.py
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

WINDOWS = (50, 100, 150, 200, 250)


def robot_weights(p: pd.DataFrame, mix: dict[str, float], window: int) -> pd.DataFrame:
    on = st.trend_sma(p[list(mix)], window) > 0
    w = pd.DataFrame(0.0, index=p.index, columns=p.columns)
    for t, share in mix.items():
        w[t] = on[t] * 0.30 * share
    w["ACWI"] = 0.70
    return w


def walk_forward(p: pd.DataFrame, mix: dict[str, float]) -> tuple[pd.Series, list[str]]:
    """Chaque 1er janvier : choisir la durée de moyenne qui a eu le meilleur Sharpe sur les 3 ans
    précédents, l'appliquer à l'année qui commence (sans regarder cette année)."""
    curves = {w: bt.run(p, robot_weights(p, mix, w)) for w in WINDOWS}
    pieces, log = [], []
    for year in range(2021, p.index[-1].year + 1):
        train = slice(f"{year - 3}-01-01", f"{year - 1}-12-31")
        best = max(WINDOWS, key=lambda w: bt.metrics(curves[w][train])["sharpe"])
        seg = curves[best][f"{year - 1}-12-31":f"{year}-12-31"]
        pieces.append(seg.pct_change().dropna())
        log.append(f"{year}: SMA{best}")
    return (1 + pd.concat(pieces)).cumprod(), log


def main():
    raw = load_prices(["ACWI", "BTC-USD", "ETH-USD"], start="2014-01-01")
    p, fixed = clean_spikes(daily(raw).loc["2017-11-09":].dropna())
    mixes = {"BTC seul": {"BTC-USD": 1.0},
             "BTC+ETH 50/50 (robot actuel)": {"BTC-USD": 0.5, "ETH-USD": 0.5},
             "BTC 2/3 + ETH 1/3": {"BTC-USD": 2 / 3, "ETH-USD": 1 / 3}}
    md = ["# Satellite crypto : BTC seul ou BTC+ETH ? (portefeuille complet 70 % ACWI + 30 % crypto)", "",
          f"Frais 0,20 %. Données corrigées : {fixed or 'aucune'}.", "",
          "## 1. Réglage fixe SMA150", "",
          "| Satellite | Période | Rendement/an | Perte max | Sharpe |", "|---|---|---|---|---|"]
    yearly = {}
    for name, mix in mixes.items():
        eq = bt.run(p, robot_weights(p, mix, 150))
        yearly[name] = eq.resample("YE").last().pct_change()
        for lab, part in (("2018-07 → 2020", eq["2018-07-01":"2020-12-31"]), ("2021+", eq["2021-01-01":])):
            m = bt.metrics(part / part.iloc[0])
            md.append(f"| {name} | {lab} | {m['rendement_annuel']:+.1%} | {m['perte_max']:.1%} | {m['sharpe']:.2f} |")

    y = pd.DataFrame(yearly).dropna()
    y.index = y.index.year
    md += ["", "## 2. Année par année (SMA150)", "", "| Année | " + " | ".join(mixes) + " |",
           "|---" * (len(mixes) + 1) + "|"]
    md += [f"| {a} | " + " | ".join(f"{v:+.1%}" for v in r) + " |" for a, r in y.iterrows()]
    wins = (y["BTC seul"] > y["BTC+ETH 50/50 (robot actuel)"]).sum()
    md += ["", f"BTC seul bat BTC+ETH **{wins} années sur {len(y)}**.", ""]

    md += ["## 3. Test glissant 2021+ (réglage choisi chaque année sur les 3 ans passés)", "",
           "| Satellite | Glissant : rendement/an | Perte max | Sharpe | Fixe SMA150 : Sharpe | Réglages choisis |",
           "|---|---|---|---|---|---|"]
    for name, mix in mixes.items():
        wf, log = walk_forward(p, mix)
        m = bt.metrics(wf)
        fx = bt.run(p, robot_weights(p, mix, 150))["2021-01-01":]
        mf = bt.metrics(fx / fx.iloc[0])
        md.append(f"| {name} | {m['rendement_annuel']:+.1%} | {m['perte_max']:.1%} | {m['sharpe']:.2f} | "
                  f"{mf['sharpe']:.2f} | {', '.join(log)} |")
    out = "\n".join(md) + "\n"
    Path(__file__).parent.joinpath("training_sleeve_results.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
