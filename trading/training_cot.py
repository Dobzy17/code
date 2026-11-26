"""Hors marché : positions extrêmes des gros spéculateurs (rapport COT de la CFTC) et retournements.
Indice COT 3 ans = position nette des spéculateurs (en % des contrats ouverts) rapportée à son min/max sur 156 semaines.
« Achat encombré » : indice > 90 ; « vente encombrée » : indice < 10 (lecture « à contre-courant » de J. Shapiro).
Le rapport (positions du mardi) est publié le vendredi : rendements mesurés à partir du lundi suivant.
Usage : python3 trading/training_cot.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd
import requests

from data import load_prices

MARKETS = {"Or": ("088691", "GC=F"), "Pétrole WTI": ("067651", "CL=F"), "S&P 500": ("13874A", "ES=F")}


def cot_history(code: str) -> pd.Series:
    r = requests.get("https://publicreporting.cftc.gov/resource/6dca-aqww.json", timeout=120, params={
        "$where": f"cftc_contract_market_code='{code}'", "$order": "report_date_as_yyyy_mm_dd ASC", "$limit": 5000,
        "$select": "report_date_as_yyyy_mm_dd,noncomm_positions_long_all,noncomm_positions_short_all,open_interest_all"})
    r.raise_for_status()
    d = pd.DataFrame(r.json())
    d.index = pd.to_datetime(d.pop("report_date_as_yyyy_mm_dd"))
    d = d.astype(float)
    return (d.noncomm_positions_long_all - d.noncomm_positions_short_all) / d.open_interest_all


def main():
    md = ["# Positions extrêmes des spéculateurs (COT) : signal de retournement ?", "",
          "| Marché | Situation | Semaines | +4 sem. (médiane) | +12 sem. | +26 sem. | % positif à 12 sem. |", "|---|---|---|---|---|---|---|"]
    for name, (code, fut) in MARKETS.items():
        net = cot_history(code)
        idx = (net - net.rolling(156).min()) / (net.rolling(156).max() - net.rolling(156).min()) * 100
        px = load_prices([fut], start="2000-01-01")[fut].dropna()
        avail = idx.index + pd.Timedelta(days=6)          # mardi + 6 j = lundi suivant (publication le vendredi)
        sig = pd.Series(idx.values, index=avail).dropna()
        sig = sig[sig.index >= px.index[0]]
        entry = px.reindex(sig.index, method="bfill")
        def fwd(weeks):
            later = px.reindex(sig.index + pd.Timedelta(weeks=weeks), method="bfill")
            return pd.Series(later.values / entry.values - 1, index=sig.index)
        f = {w: fwd(w) for w in (4, 12, 26)}
        for lab, mask in (("Toutes les semaines", sig.notna()), ("Achat encombré (> 90)", sig > 90),
                          ("Vente encombrée (< 10)", sig < 10)):
            v = {w: f[w][mask].dropna() for w in f}
            md.append(f"| {name} | {lab} | {int(mask.sum())} | {v[4].median():+.1%} | {v[12].median():+.1%} | "
                      f"{v[26].median():+.1%} | {(v[12] > 0).mean():.0%} |")
        md.append(f"| {name} | **Aujourd'hui** | indice {idx.iloc[-1]:.0f}/100 (rapport du {idx.index[-1].date()}) | | | | |")
    md += ["", "_Prix : contrats à terme en continu de Yahoo (GC=F, CL=F, ES=F), depuis 2000. Les semaines se chevauchent : "
           "les nombres de semaines surestiment le nombre de cas indépendants._"]
    out = "\n".join(md) + "\n"
    (Path(__file__).parent / "training_cot_results.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
