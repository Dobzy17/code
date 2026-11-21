"""Test sans biais du survivant : on prend les cryptos qui étaient en tête AU DÉBUT de la
période (pas celles qui existent encore aujourd'hui), y compris celles qui se sont effondrées.

Listes établies de mémoire d'après les classements par capitalisation de l'époque
(hors stablecoins) : approximatives, mais choisies sans connaître la suite.
IOTA (2018) et UNI (2021) manquent : Yahoo n'a pas leur historique.

Usage : python3 trading/training_survivor.py
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

UNIVERSES = {
    "Top début 2018": ("2018-01-01", ["BTC-USD", "XRP-USD", "ETH-USD", "BCH-USD", "ADA-USD", "LTC-USD",
                                       "XEM-USD", "XLM-USD", "TRX-USD", "DASH-USD", "NEO-USD", "EOS-USD",
                                       "XMR-USD", "BTG-USD", "QTUM-USD", "ETC-USD", "ICX-USD", "LSK-USD", "OMG-USD"]),
    "Top début 2021": ("2021-01-01", ["BTC-USD", "ETH-USD", "XRP-USD", "LTC-USD", "BCH-USD", "ADA-USD",
                                       "DOT-USD", "LINK-USD", "BNB-USD", "XLM-USD", "DOGE-USD", "BSV-USD",
                                       "EOS-USD", "XMR-USD", "TRX-USD", "XTZ-USD", "THETA-USD", "VET-USD",
                                       "CRO-USD", "ATOM-USD"]),
}


def main():
    md = ["# Test sans biais du survivant", "", "Frais 0,20 % par ordre. Poids égaux entre cryptos.", ""]
    for name, (start, tickers) in UNIVERSES.items():
        # on charge 1 an avant le départ pour que les moyennes soient prêtes au jour 1
        raw = load_prices(tickers, start="2017-01-01")
        p = daily(raw).loc[str(int(start[:4]) - 1) + "-01-01":]
        p, fixed = clean_spikes(p)
        if fixed:
            md.append(f"_Données corrigées (bonds > +300 % en un jour neutralisés) : {fixed}_")
        btc = p[["BTC-USD"]]
        cands = {
            "Achat-conservation de tout le panier": (p, st.buy_hold(p)),
            "Achat-conservation BTC seul": (btc, st.buy_hold(btc)),
            "SMA150 sur tout le panier": (p, st.trend_sma(p, 150)),
            "SMA150 BTC seul": (btc, st.trend_sma(btc, 150)),
            "Donchian ensemble, panier": (p, st.donchian_ensemble(p)),
            "Donchian + vol. cible, panier": (p, st.vol_target(st.donchian_ensemble(p), p)),
        }
        md += [f"## {name} (de {start} à aujourd'hui, {len(tickers)} cryptos)", "",
               "| Stratégie | Rendement/an | Perte max | Sharpe | ×capital |", "|---|---|---|---|---|"]
        for cname, (pp, w) in cands.items():
            eq = bt.run(pp, w).loc[start:]
            m = bt.metrics(eq / eq.iloc[0])
            md.append(f"| {cname} | {m['rendement_annuel']:+.1%} | {m['perte_max']:.1%} | {m['sharpe']:.2f} | "
                      f"×{m['multiplicateur']:.2f} |")
        last = p.iloc[-1] / p.loc[start] - 1
        md += ["", f"Cryptos du panier en perte depuis le départ : **{(last < 0).sum()} sur {len(tickers)}** "
               f"(pire : {last.idxmin()} {last.min():.0%}).", ""]
    out = "\n".join(md) + "\n"
    Path(__file__).parent.joinpath("training_survivor_results.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
