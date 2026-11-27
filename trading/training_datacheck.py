"""Les cours Yahoo sont-ils fiables ? Comparaison quotidienne avec Kraken et Binance (API publiques gratuites).

On compare les clôtures journalières (bougie UTC) et, surtout, la DÉCISION du robot
(au-dessus ou en dessous de la moyenne 150 j) selon chaque source.
Usage : python3 trading/training_datacheck.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd
import requests

from data import load_prices

KRAKEN = {"BTC-USD": "XBTUSD", "ETH-USD": "ETHUSD"}
BINANCE = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT"}


def kraken(pair: str) -> pd.Series:
    r = requests.get("https://api.kraken.com/0/public/OHLC", params={"pair": pair, "interval": 1440}, timeout=30)
    r.raise_for_status()
    js = r.json()
    if js.get("error"):
        raise RuntimeError(js["error"])
    rows = next(v for k, v in js["result"].items() if k != "last")
    s = pd.Series({pd.to_datetime(int(x[0]), unit="s"): float(x[4]) for x in rows})
    return s.iloc[:-1]  # la dernière bougie est encore en cours


def binance(symbol: str) -> pd.Series:
    r = requests.get("https://data-api.binance.vision/api/v3/klines",
                     params={"symbol": symbol, "interval": "1d", "limit": 1000}, timeout=30)
    r.raise_for_status()
    s = pd.Series({pd.to_datetime(int(x[0]), unit="ms"): float(x[4]) for x in r.json()})
    return s.iloc[:-1]


def main():
    yahoo = load_prices(list(KRAKEN), start="2022-01-01", max_age_hours=2)
    md = ["# Fiabilité des données : Yahoo contre Kraken et Binance", "",
          "Écart = |Yahoo − source| / source, sur la clôture journalière UTC. "
          "Binance cote en USDT (pas en dollars) : un petit écart y est normal.", "",
          "| Actif | Source | Jours comparés | Écart médian | Écart max (date) | Jours > 1 % | "
          "Décisions SMA150 différentes |", "|---|---|---|---|---|---|---|"]
    for t in KRAKEN:
        y = yahoo[t].dropna()
        for name, fetch, code in (("Kraken", kraken, KRAKEN[t]), ("Binance", binance, BINANCE[t])):
            try:
                o = fetch(code)
            except Exception as e:
                md.append(f"| {t} | {name} | indisponible : {e} | | | | |")
                continue
            both = pd.concat([y.rename("y"), o.rename("o")], axis=1, sort=True).dropna()
            diff = (both.y / both.o - 1).abs()
            # signal calculé sur la série de chaque source (fenêtre complète nécessaire)
            sig_y = both.y > both.y.rolling(150).mean()
            sig_o = both.o > both.o.rolling(150).mean()
            valid = both.y.rolling(150).mean().notna()
            disagree = int((sig_y != sig_o)[valid].sum())
            md.append(f"| {t} | {name} | {len(both)} ({both.index[0].date()} → {both.index[-1].date()}) | "
                      f"{diff.median():.3%} | {diff.max():.2%} ({diff.idxmax().date()}) | {(diff > 0.01).sum()} | "
                      f"{disagree} sur {int(valid.sum())} |")
    out = "\n".join(md) + "\n"
    Path(__file__).parent.joinpath("training_datacheck_results.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
