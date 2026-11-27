"""Recherche : quelles stratégies tiennent la route, avant et après 2021 ?

Usage : python3 trading/research.py
La période 2021+ n'a servi à choisir AUCUN paramètre : c'est le test « hors échantillon ».
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd

import backtest as bt
import strategies as st
from data import load_prices

SPLIT = "2021-01-01"
CRYPTO = ["BTC-USD", "ETH-USD"]
STOCKS = ["SPY", "EFA", "IEF"]


def daily(prices: pd.DataFrame) -> pd.DataFrame:
    """Calendrier commun 7j/7 : les actions gardent leur dernier cours le week-end."""
    idx = pd.date_range(prices.index.min(), prices.index.max(), freq="D")
    return prices.reindex(idx).ffill()


def report(name, prices, weights, out):
    eq = bt.run(prices, weights)
    for label, part in (("avant 2021 (choix)", eq[:SPLIT]), ("2021+ (hors échantillon)", eq[SPLIT:])):
        part = part / part.iloc[0]
        line = f"{name:<32} {label:<26} {bt.fmt(bt.metrics(part))}"
        print(line); out.append(line)


def main():
    out: list[str] = []
    crypto = daily(load_prices(CRYPTO, start="2014-01-01")).loc["2018-01-01":].dropna()
    stocks = daily(load_prices(STOCKS, start="2010-01-01")).loc["2014-01-01":].dropna()

    print("\n=== CRYPTO (BTC + ETH) ===")
    report("achat-conservation", crypto, st.buy_hold(crypto), out)
    for w in (50, 100, 150, 200, 250):   # robustesse : le résultat ne doit pas dépendre d'UN réglage
        report(f"tendance SMA{w}", crypto, st.trend_sma(crypto, w), out)

    print("\n=== ACTIONS / OBLIGATIONS (SPY, EFA, IEF) ===")
    spy = stocks[["SPY"]]
    report("achat-conservation SPY", spy, st.buy_hold(spy), out)
    report("tendance SMA200 SPY", spy, st.trend_sma(spy, 200), out)
    for lb in (126, 252, 365):
        report(f"momentum dual {lb}j", stocks, st.dual_momentum(stocks, ["SPY", "EFA"], "IEF", lb), out)

    print("\n=== PORTEFEUILLE DU ROBOT : 70 % ACWI + 30 % crypto (tendance SMA150) ===")
    allp = daily(load_prices(["ACWI"] + CRYPTO, start="2014-01-01")).loc["2018-01-01":].dropna()
    w_bot = st.trend_sma(allp[CRYPTO], 150) * 0.30
    w_bot["ACWI"] = 0.70
    w_bh = pd.DataFrame({"ACWI": 0.70, "BTC-USD": 0.15, "ETH-USD": 0.15}, index=allp.index)
    report("70/30 sans règle", allp, w_bh, out)
    report("robot 70/30 + tendance", allp, w_bot[allp.columns], out)
    report("100 % ACWI", allp[["ACWI"]], st.buy_hold(allp[["ACWI"]]), out)

    Path(__file__).parent.joinpath("research_results.txt").write_text("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
