"""Après impôts (France) : (1) PEA contre compte-titres pour le cœur ETF ; (2) crypto avec la règle de tendance :
vendre en EUROS à chaque signal (impôt chaque année) contre vendre en STABLECOIN (impôt seulement au retrait final).

Hypothèses (à vérifier sur impots.gouv.fr, les sources divergent) :
  * flat tax 30 % (12,8 % d'impôt + 17,2 % de prélèvements sociaux) ; variante 31,4 % si la hausse de CSG 2026 s'applique ;
  * PEA de plus de 5 ans : seuls les prélèvements sociaux (17,2 %) sur le gain, au retrait ;
  * crypto : moins-values imputables seulement sur les plus-values de la même année (pas de report).
Usage : python3 trading/training_tax.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd

import strategies as st
from data import clean_spikes, load_prices
from research import daily

COST = 0.002


def core_table() -> list[str]:
    md = ["## 1. Cœur ETF : PEA contre compte-titres (ETF capitalisant, aucune vente avant la fin)", "",
          "| Durée | Rendement brut/an | Capital final avant impôt (10 000 €) | Net PEA (17,2 %) | Net compte-titres (30 %) | Gain du PEA |",
          "|---|---|---|---|---|---|"]
    for years in (5, 10, 20, 30):
        for r in (0.05, 0.08):
            final = 10_000 * (1 + r) ** years
            gain = final - 10_000
            pea, cto = final - 0.172 * gain, final - 0.30 * gain
            md.append(f"| {years} ans | {r:.0%} | {final:,.0f} € | {pea:,.0f} € | {cto:,.0f} € | +{pea - cto:,.0f} € |")
    return md


def crypto_sim(p: pd.DataFrame, tax: float, to_euro: bool) -> tuple[float, float]:
    """Satellite BTC/ETH 50/50 avec SMA150 et zone de 3 %. Renvoie (capital final net, impôts payés)."""
    w = st.trend_band(p, 150, 0.03).shift(1).fillna(0.0) > 0      # exécution le lendemain
    cash = {t: 5_000.0 for t in p.columns}
    qty = {t: 0.0 for t in p.columns}
    basis = {t: 0.0 for t in p.columns}
    year_pnl, taxes, year = 0.0, 0.0, p.index[0].year
    for d in p.index:
        if d.year != year:                      # fin d'année : impôt sur le solde des ventes en euros
            if to_euro and year_pnl > 0:
                t_amt = tax * year_pnl
                taxes += t_amt
                for t in cash:
                    cash[t] -= t_amt / 2
            year_pnl, year = 0.0, d.year
        for t in p.columns:
            px = p.at[d, t]
            if w.at[d, t] and qty[t] == 0 and cash[t] > 0:
                qty[t] = cash[t] * (1 - COST) / px
                basis[t] = cash[t]
                cash[t] = 0.0
            elif not w.at[d, t] and qty[t] > 0:
                proceeds = qty[t] * px * (1 - COST)
                year_pnl += proceeds - basis[t]
                cash[t], qty[t], basis[t] = proceeds, 0.0, 0.0
    final = sum(cash[t] + qty[t] * p[t].iloc[-1] * (1 - COST) for t in p.columns)
    if to_euro:
        open_gain = sum(qty[t] * p[t].iloc[-1] * (1 - COST) - basis[t] for t in p.columns if qty[t] > 0)
        last = max(year_pnl + open_gain, 0) * tax
    else:
        last = max(final - 10_000.0, 0) * tax     # un seul impôt au retrait final
    return final - last, taxes + last


def main():
    md = ["# Après impôts (France)", ""] + core_table()
    p, _ = clean_spikes(daily(load_prices(["BTC-USD", "ETH-USD"], start="2014-01-01")).loc["2018-01-01":].dropna())
    md += ["", f"## 2. Satellite crypto avec la règle de tendance, 10 000 de départ, {p.index[0].date()} → {p.index[-1].date()} "
           "(premiers achats possibles après 150 jours ; cours en dollars, comptés comme des euros : seul l'écart entre méthodes compte)",
           "", "| Méthode | Taux | Capital final net | Impôts payés | Écart avec stablecoin |", "|---|---|---|---|---|"]
    for tax in (0.30, 0.314):
        sc, sc_tax = crypto_sim(p, tax, to_euro=False)
        eu, eu_tax = crypto_sim(p, tax, to_euro=True)
        md.append(f"| Vente en stablecoin (impôt au retrait final) | {tax:.1%} | {sc:,.0f} € | {sc_tax:,.0f} € | — |")
        md.append(f"| Vente en euros à chaque signal (impôt chaque année) | {tax:.1%} | {eu:,.0f} € | {eu_tax:,.0f} € | "
                  f"{eu / sc - 1:+.0%} |")
    md += ["", "_Limites : la formule fiscale crypto française (prix total d'acquisition du portefeuille) est simplifiée ici en "
           "« gain de chaque aller-retour », ce qui est exact quand on sort entièrement d'un actif. Le stablecoin est supposé "
           "garder sa parité (risque testé séparément)._"]
    out = "\n".join(md) + "\n"
    (Path(__file__).parent / "training_tax_results.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
