"""Autres marchés : le « carry trade » sur devises. Chaque mois : acheter les 2 devises du G10 aux taux d'intérêt les plus élevés,
vendre les 2 aux taux les plus bas, encaisser la différence de taux + la variation des changes.
Taux à 3 mois de l'OCDE (FRED, mensuels) utilisés avec 1 mois de retard (date de publication). Frais 0,10 % par changement de position.
C'est un pari à effet de levier, inaccessible au particulier français autrement que par des CFD (produits que l'AMF déconseille).
Usage : python3 trading/training_carry.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd

import backtest as bt
from data import load_prices
from training_curve import fred

FX = {"AUD": ("AUDUSD=X", False), "NZD": ("NZDUSD=X", False), "EUR": ("EURUSD=X", False), "GBP": ("GBPUSD=X", False),
      "JPY": ("USDJPY=X", True), "CHF": ("USDCHF=X", True), "CAD": ("USDCAD=X", True), "USD": (None, False)}
RATE = {"AUD": "IR3TIB01AUM156N", "NZD": "IR3TIB01NZM156N", "EUR": "IR3TIB01EZM156N", "GBP": "IR3TIB01GBM156N",
        "JPY": "IR3TIB01JPM156N", "CHF": "IR3TIB01CHM156N", "CAD": "IR3TIB01CAM156N", "USD": "IR3TIB01USM156N"}


def main():
    px = load_prices([v[0] for v in FX.values() if v[0]], start="2003-01-01")
    usd_val = pd.DataFrame(index=px.index)                      # valeur de 1 unité de devise en dollars
    for c, (t, inv) in FX.items():
        usd_val[c] = 1.0 if t is None else (1 / px[t] if inv else px[t])
    usd_val = usd_val.ffill().dropna()
    mret = usd_val.resample("ME").last().pct_change()
    rates = pd.DataFrame({c: fred(s) for c, s in RATE.items()}).resample("ME").last().ffill() / 100
    rates = rates.shift(1)                                        # connu le mois suivant
    rates = rates.reindex(mret.index).ffill()
    out_r = []
    for d in mret.index[1:]:
        r = rates.loc[d].dropna()
        if len(r) < 8:
            continue
        hi, lo = r.nlargest(2).index, r.nsmallest(2).index
        prev = rates.index[rates.index.get_loc(d) - 1]
        rp = rates.loc[prev]
        ret = (mret.loc[d, hi].mean() + rp[hi].mean() / 12) - (mret.loc[d, lo].mean() + rp[lo].mean() / 12) - 0.001
        out_r.append((d, ret, list(hi), list(lo)))
    s = pd.Series({d: r for d, r, _, _ in out_r})
    eq = (1 + s).cumprod()
    md = ["# Carry trade G10 (long 2 devises à taux haut, short 2 à taux bas), sans effet de levier", "",
          f"{s.index[0].date()} → {s.index[-1].date()}, {len(s)} mois.", "",
          "| Période | Rendement/an | Perte max | Sharpe | Pire mois |", "|---|---|---|---|---|"]
    for lab, a, b in (("Tout", None, None), ("2003-2012", None, "2012-12-31"), ("2013+", "2013-01-01", None)):
        x = eq[a:b]
        x = x / x.iloc[0]
        rr = s[a:b]
        dd = (x / x.cummax() - 1).min()
        cagr = x.iloc[-1] ** (12 / len(rr)) - 1
        sh = rr.mean() / rr.std() * 12 ** 0.5
        md.append(f"| {lab} | {cagr:+.1%} | {dd:.0%} | {sh:.2f} | {rr.min():+.1%} |")
    y = s.groupby(s.index.year).apply(lambda v: (1 + v).prod() - 1)
    md += ["", "Années : " + ", ".join(f"{k} {v:+.0%}" for k, v in y.items()), "",
           f"Position actuelle : achat {', '.join(out_r[-1][2])} / vente {', '.join(out_r[-1][3])}."]
    out = "\n".join(md) + "\n"
    (Path(__file__).parent / "training_carry_results.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
