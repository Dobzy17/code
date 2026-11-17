"""Faux signaux (« whipsaws ») de la règle SMA150 : combien, quand, et à quel coût ?

Chaque trade = une période continue au-dessus de la moyenne (achat au signal, vente au signal inverse),
exécution le lendemain du signal, frais 0,20 % à l'achat et à la vente.
Usage : python3 trading/training_whipsaw.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd

from data import clean_spikes, load_prices
from research import daily

COST = 0.002


def trades(s: pd.Series, window: int = 150) -> pd.DataFrame:
    on = (s > s.rolling(window).mean()).astype(int)
    held = on.shift(1).fillna(0)                  # exécution le lendemain
    change = held.diff().fillna(held)
    entries, exits = list(s.index[change == 1]), list(s.index[change == -1])
    out = []
    for i, e in enumerate(entries):
        x = next((d for d in exits if d > e), None)
        end = x if x is not None else s.index[-1]
        ret = s[end] / s[e] * (1 - COST) ** 2 - 1  # prix à l'entrée et à la sortie (clôture du jour d'exécution)
        out.append({"entree": e, "sortie": end, "jours": (end - e).days, "rendement": ret, "ouvert": x is None})
    return pd.DataFrame(out)


def main():
    p, _ = clean_spikes(daily(load_prices(["BTC-USD", "ETH-USD"], start="2014-01-01")).loc["2017-11-09":])
    md = ["# Faux signaux de la règle SMA150", "", "Frais 0,20 % à l'achat et à la vente.", ""]
    for t in p.columns:
        tr = trades(p[t].dropna())
        tr = tr[tr.entree >= "2018-07-01"]
        short = tr[tr.jours < 30]
        wins = tr[tr.rendement > 0]
        md += [f"## {t} : {len(tr)} trades depuis mi-2018", "",
               f"- Gagnants : **{len(wins)} sur {len(tr)}** ({len(wins) / len(tr):.0%}). "
               f"Gain moyen d'un gagnant : {wins.rendement.mean():+.1%} ; perte moyenne d'un perdant : "
               f"{tr[tr.rendement <= 0].rendement.mean():+.1%}.",
               f"- Meilleur trade : {tr.rendement.max():+.0%} ({tr.loc[tr.rendement.idxmax(), 'entree'].date()}, "
               f"{tr.loc[tr.rendement.idxmax(), 'jours']} jours).",
               f"- Faux signaux (trades de moins de 30 jours) : **{len(short)}**, dont {int((short.rendement <= 0).sum())} perdants ; "
               f"coût cumulé de ces faux signaux : **{((1 + short.rendement).prod() - 1):+.1%}**.",
               f"- Les 3 meilleurs trades rapportent à eux seuls ×{(1 + tr.rendement.nlargest(3)).prod():.1f} ; "
               f"tous les autres trades ensemble : ×{(1 + tr.rendement.drop(tr.rendement.nlargest(3).index)).prod():.2f}.",
               "", "| Année | Trades | Faux signaux (<30 j) | Résultat des trades ouverts cette année |", "|---|---|---|---|"]
        for y, g in tr.groupby(tr.entree.dt.year):
            md.append(f"| {y} | {len(g)} | {int((g.jours < 30).sum())} | {((1 + g.rendement).prod() - 1):+.0%} |")
        md.append("")
    out = "\n".join(md) + "\n"
    Path(__file__).parent.joinpath("training_whipsaw_results.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
