"""Zone tampon contre les faux signaux : X = 0, 1, 2, 3, 5 %. Retenue seulement si TOUTE la plage aide.
Usage : python3 trading/training_band.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import backtest as bt
import strategies as st
from data import clean_spikes, load_prices
from research import daily

BANDS = (0.0, 0.01, 0.02, 0.03, 0.05)


def main():
    raw = load_prices(["ACWI", "BTC-USD", "ETH-USD"], start="2014-01-01")
    p, _ = clean_spikes(daily(raw).loc["2017-11-09":].dropna())
    c = p[["BTC-USD", "ETH-USD"]]
    md = ["# Zone tampon contre les faux signaux (SMA150)", "",
          "Portefeuille complet (70 % ACWI + 30 % BTC/ETH), frais 0,20 %.", "",
          "| Zone | Période | Rendement/an | Perte max | Sharpe | Nb d'ordres crypto |", "|---|---|---|---|---|---|"]
    for b in BANDS:
        w = st.trend_band(c, 150, b) * 0.30
        w["ACWI"] = 0.70
        eq = bt.run(p, w[p.columns])
        n_orders = int((w[["BTC-USD", "ETH-USD"]].diff().abs() > 0).sum().sum())
        for lab, part in (("2018-07 → 2020", eq["2018-07-01":"2020-12-31"]), ("2021+", eq["2021-01-01":])):
            m = bt.metrics(part / part.iloc[0])
            md.append(f"| {b:.0%} | {lab} | {m['rendement_annuel']:+.1%} | {m['perte_max']:.1%} | "
                      f"{m['sharpe']:.2f} | {n_orders} |")
    near = ((c / c.rolling(150).mean() - 1).abs() < 0.02)["2018-07-01":]
    md += ["", f"Jours où le cours est à moins de 2 % de sa moyenne (zone fragile, leçon 17) : "
           f"BTC {near['BTC-USD'].mean():.0%}, ETH {near['ETH-USD'].mean():.0%} des jours."]
    out = "\n".join(md) + "\n"
    Path(__file__).parent.joinpath("training_band_results.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
