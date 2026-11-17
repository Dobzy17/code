"""Clôtures journalières TERMINÉES depuis l'API publique de Kraken (gratuite, sans clé).
Corrige la leçon 17 : Yahoo n'a pas encore la bougie de la veille à 3h13."""
from __future__ import annotations

import pandas as pd
import requests

PAIRS = {"BTC-USD": "XBTUSD", "ETH-USD": "ETHUSD", "BTC-EUR": "XBTEUR", "ETH-EUR": "ETHEUR"}


def daily_closes(ticker: str) -> pd.Series:
    r = requests.get("https://api.kraken.com/0/public/OHLC",
                     params={"pair": PAIRS[ticker], "interval": 1440}, timeout=30)
    r.raise_for_status()
    js = r.json()
    if js.get("error"):
        raise RuntimeError(f"Kraken : {js['error']}")
    rows = next(v for k, v in js["result"].items() if k != "last")
    s = pd.Series({pd.to_datetime(int(x[0]), unit="s"): float(x[4]) for x in rows}, name=ticker)
    return s.iloc[:-1]  # la dernière bougie est en cours : on ne l'utilise jamais
