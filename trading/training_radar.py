"""Radar de tous les marchés : chaque fin de mois, détenir les 5 marchés (parmi ~45 ETF) à la plus forte tendance
sur 12 mois, chacun seulement s'il est au-dessus de sa moyenne 150 jours (sinon cash).
Un ETF n'est éligible qu'après 13 mois d'existence : pas de biais du survivant sur les dates de lancement.
Usage : python3 trading/training_radar.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd

import backtest as bt
from data import clean_spikes, load_prices

UNIVERSE = {
    "Actions pays": ["SPY", "QQQ", "IWM", "EFA", "VGK", "EWQ", "EWG", "EWU", "EWJ", "INDA", "FXI", "MCHI", "EWZ",
                     "EEM", "EWY", "EWT", "EWC", "EWA"],
    "Secteurs": ["XLK", "SMH", "XLE", "XLF", "XLV", "XLI", "XLP", "XLU", "XLY", "XLB", "ITA", "XBI"],
    "Matières premières": ["USO", "CPER", "URA", "SLV", "GLD", "DBA", "DBC", "UNG"],
    "Obligations": ["TLT", "IEF", "LQD", "HYG", "EMB", "TIP"],
    "Immobilier": ["VNQ"],
}
TICKERS = [t for v in UNIVERSE.values() for t in v]
P = 252


def radar_weights(p: pd.DataFrame, top: int = 5, lookback: int = 252, sma: int | None = 150) -> tuple[pd.DataFrame, dict]:
    mom = p / p.shift(lookback) - 1
    above = p > p.rolling(sma).mean() if sma else p.notna()
    age = p.notna().cumsum()
    ends = p.index.to_series().groupby(p.index.to_period("M")).max().values
    w = pd.DataFrame(float("nan"), index=p.index, columns=p.columns)
    picks = {}
    for d in ends:
        elig = mom.loc[d][(age.loc[d] >= 273) & mom.loc[d].notna()]
        if len(elig) < top:
            continue
        best = elig.nlargest(top).index
        row = pd.Series(0.0, index=p.columns)
        held = [t for t in best if above.loc[d, t]]
        row[held] = 1 / top
        w.loc[d] = row
        picks[d] = list(best)
    return w.ffill().fillna(0.0), picks


def after_tax_cto(eq: pd.Series, rate: float = 0.30) -> float:
    """Approximation prudente : impôt chaque année sur le gain de l'année (rotation mensuelle = gains réalisés)."""
    y = eq.resample("YE").last()
    y = pd.concat([pd.Series([eq.iloc[0]], index=[eq.index[0]]), y])
    capital = 1.0
    for r in y.pct_change().dropna():
        capital *= 1 + r * (1 - rate) if r > 0 else 1 + r
    return capital


def main():
    raw, fixed = clean_spikes(load_prices(TICKERS + ["ACWI"], start="2000-01-01"))
    p = raw[TICKERS].loc["2005-01-01":]
    p = p.dropna(how="all")
    w, picks = radar_weights(p)
    eq = bt.run(p.fillna(0), w)
    acwi = raw["ACWI"].dropna()
    md = ["# Radar de tous les marchés (top 5 sur ~45 ETF, rééquilibrage mensuel, sortie sous la moyenne 150 j)", "",
          f"{len(TICKERS)} ETF. Frais 0,20 %. Données corrigées : {fixed or 'aucune'}.", "",
          "| Stratégie | 2009-2015 | 2016+ | Perte max 2009+ | Sharpe 2016+ | Multiplicateur 2009+ |",
          "|---|---|---|---|---|---|"]

    def row(name, e):
        a = e["2009-01-01":"2015-12-31"]
        b = e["2016-01-01":]
        f = e["2009-01-01":]
        ma, mb, mf = (bt.metrics(x / x.iloc[0], P) for x in (a, b, f))
        md.append(f"| {name} | {ma['rendement_annuel']:+.1%} | {mb['rendement_annuel']:+.1%} | {mf['perte_max']:.0%} | "
                  f"{mb['sharpe']:.2f} | ×{mf['multiplicateur']:.2f} |")
        return f

    e_acwi = bt.run(acwi.to_frame(), pd.DataFrame(1.0, index=acwi.index, columns=["ACWI"]))
    fa = row("ETF monde (ACWI), sans rien faire", e_acwi)
    fr = row("Radar top 5 + sortie", eq)
    for top in (3, 10):
        row(f"Radar top {top} + sortie (robustesse)", bt.run(p.fillna(0), radar_weights(p, top=top)[0]))
    w_nosma, _ = radar_weights(p, sma=None)
    row("Radar top 5 sans règle de sortie", bt.run(p.fillna(0), w_nosma))

    acwi_pea = 1 + (fa.iloc[-1] / fa.iloc[0] - 1) * (1 - 0.172)
    radar_cto = after_tax_cto(fr / fr.iloc[0])
    md += ["", f"**Après impôts (2009 → aujourd'hui, 1 € placé)** : ETF monde dans un PEA, impôt au retrait (17,2 %) → "
           f"**{acwi_pea:.2f} €** ; radar sur compte-titres, impôt de 30 % chaque année → **{radar_cto:.2f} €**.", ""]
    last = max(picks)
    cur = w.iloc[-1]
    md += [f"## Ce que le radar détiendrait aujourd'hui (classement du {pd.Timestamp(last).date()})", "",
           ", ".join(f"{t} {'(investi)' if cur[t] > 0 else '(sous sa moyenne : cash)'}" for t in picks[last]), ""]
    sel = pd.Series([t for v in picks.values() for t in v]).value_counts().head(10)
    md += ["Marchés les plus souvent choisis depuis 2006 : " + ", ".join(f"{t} ({n} mois)" for t, n in sel.items())]
    out = "\n".join(md) + "\n"
    (Path(__file__).parent / "training_radar_results.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
