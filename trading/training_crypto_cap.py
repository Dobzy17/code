"""Deux comptes séparés : plafonner la part crypto (Kraken) à 40 % ou 50 % du total, en vendant l'excédent en euros
une fois par an (début janvier), avec 30 % d'impôt sur la plus-value réalisée, puis en versant le net sur le PEA.
Comparé à « laisser dériver » (leçon 50). Impôt final : 30 % sur la plus-value Kraken restante, 17,2 % sur celle du PEA.
Usage : python3 trading/training_crypto_cap.py
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

COST, TAX_CRYPTO, TAX_PEA = 0.002, 0.30, 0.172


def simulate(p: pd.DataFrame, cap: float | None, start: float = 10_000.0):
    crypto = ["BTC-USD", "ETH-USD"]
    on = (st.trend_band(p[crypto], 150, 0.03) > 0).shift(1).fillna(False)
    u = {"ACWI": start * 0.70 * (1 - COST) / p["ACWI"].iloc[0], "BTC-USD": 0.0, "ETH-USD": 0.0}
    stable = start * 0.30
    basis_kr, basis_pea, taxes = start * 0.30, start * 0.70, 0.0
    eq, share = [], []
    for i, d in enumerate(p.index):
        px = p.loc[d]
        kr = stable + sum(u[c] * px[c] for c in crypto)
        for c in crypto:                                     # règle de tendance à l'intérieur du compte Kraken
            tgt = kr / 2 if on.loc[d, c] else 0.0
            cur = u[c] * px[c]
            if (tgt == 0 and u[c] > 0) or (tgt > 0 and u[c] == 0) or (tgt > 0 and abs(tgt - cur) / kr > 0.10):
                diff = tgt - cur
                if diff > 0:
                    diff = min(diff, stable / (1 + COST))
                u[c] = 0.0 if tgt == 0 else u[c] + diff / px[c]
                stable -= diff + abs(diff) * COST
        kr = stable + sum(u[c] * px[c] for c in crypto)
        pea = u["ACWI"] * px["ACWI"]
        new_year = i > 0 and d.year != p.index[i - 1].year
        if cap is not None and new_year and kr / (kr + pea) > cap:
            excess = kr - cap * (kr + pea)
            frac = excess / kr
            gain = max(excess - basis_kr * frac, 0.0)
            tax = TAX_CRYPTO * gain
            taxes += tax
            for c in crypto:
                u[c] *= 1 - frac
            stable *= 1 - frac
            basis_kr *= 1 - frac
            net = excess * (1 - COST) - tax
            u["ACWI"] += net * (1 - COST) / px["ACWI"]
            basis_pea += net
        kr = stable + sum(u[c] * px[c] for c in crypto)
        pea = u["ACWI"] * px["ACWI"]
        eq.append(kr + pea)
        share.append(kr / (kr + pea))
    final_net = kr - TAX_CRYPTO * max(kr - basis_kr, 0) + pea - TAX_PEA * max(pea - basis_pea, 0)
    return pd.Series(eq, index=p.index), pd.Series(share, index=p.index), final_net, taxes


def main():
    raw, _ = clean_spikes(load_prices(["ACWI", "BTC-USD", "ETH-USD"], start="2014-01-01"))
    p = daily(raw).loc["2017-11-09":].dropna()
    md = ["# Plafond de la part crypto dans le montage à deux comptes (PEA + Kraken)", "",
          f"{p.index[0].date()} → {p.index[-1].date()}, 10 000 au départ, sans versement.", "",
          "| Plafond | Capital avant impôt final | Net après tous les impôts | Impôts payés en route | Perte max | Part crypto max / fin |",
          "|---|---|---|---|---|---|"]
    for cap in (None, 0.50, 0.40, 0.30):
        eq, sh, net, taxes = simulate(p, cap)
        m = bt.metrics(eq.iloc[150:] / eq.iloc[150])
        md.append(f"| {'aucun (dérive)' if cap is None else f'{cap:.0%}'} | {eq.iloc[-1]:,.0f} | **{net:,.0f}** | {taxes:,.0f} | "
                  f"{m['perte_max']:.0%} | {sh.max():.0%} / {sh.iloc[-1]:.0%} |")
    out = "\n".join(md) + "\n"
    (Path(__file__).parent / "training_crypto_cap_results.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
