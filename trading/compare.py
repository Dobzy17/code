"""Compare le robot depuis son départ (12/11/2026) à deux références, avec les mêmes cours que lui.
Base : clôtures du 11/11/2026 (veille du premier ordre). Ajoute une ligne à state/comparaison.csv.
Usage : python3 trading/compare.py
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd

from data import load_prices
from live.kraken_data import daily_closes

BASE = "2026-11-11"
START = 10_000.0
ROOT = Path(__file__).parent


def main():
    acwi = load_prices(["ACWI"], start="2026-10-01", max_age_hours=2)["ACWI"].dropna()
    px = {"ACWI": acwi}
    for t in ("BTC-USD", "ETH-USD"):
        px[t] = daily_closes(t)
    r = {t: s.iloc[-1] / s.loc[:BASE].iloc[-1] - 1 for t, s in px.items()}
    eq = pd.read_csv(ROOT / "state" / "equity.csv", header=None, names=["date", "equity"])
    robot = eq.equity.iloc[-1] / START - 1
    mix = 0.70 * r["ACWI"] + 0.15 * r["BTC-USD"] + 0.15 * r["ETH-USD"]
    crypto = 0.5 * r["BTC-USD"] + 0.5 * r["ETH-USD"]
    row = f"{date.today()},{robot:.4f},{mix:.4f},{crypto:.4f},{r['ACWI']:.4f}"
    f = ROOT / "state" / "comparaison.csv"
    if not f.exists():
        f.write_text("date,robot,70_30_sans_regle,btc_eth_sans_regle,acwi\n")
    lines = f.read_text().splitlines()
    if not lines[-1].startswith(str(date.today())):
        f.write_text("\n".join(lines + [row]) + "\n")
    print(f"Depuis le départ : robot {robot:+.2%} | 70/30 sans règle {mix:+.2%} | "
          f"BTC+ETH sans règle {crypto:+.2%} | ACWI {r['ACWI']:+.2%}  (ACWI au {acwi.index[-1].date()}, "
          f"crypto au {px['BTC-USD'].index[-1].date()})")


if __name__ == "__main__":
    main()
