"""Crypto : scénario catastrophe sur le stablecoin de refuge. Combien de temps le satellite est-il en stablecoin,
et que coûterait une perte de parité de 10 %, 30 % ou 100 % (type TerraUSD, mai 2022) au portefeuille total ?
Usage : python3 trading/training_stablecoin.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import strategies as st
from data import clean_spikes, load_prices
from research import daily


def main():
    p, _ = clean_spikes(daily(load_prices(["BTC-USD", "ETH-USD"], start="2014-01-01")).loc["2018-01-01":].dropna())
    w = st.trend_band(p, 150, 0.03).loc["2018-07-01":]          # moyenne 150 j disponible dès le départ
    p = p.loc["2018-07-01":]
    in_stable = 1 - w.sum(axis=1)                       # part du satellite en stablecoin (0 à 1)
    u = load_prices(["USDC-USD", "USDT-USD"], start="2019-01-01")
    md = ["# Scénario catastrophe : le stablecoin de refuge perd sa parité", "",
          f"Satellite crypto du robot (30 % du portefeuille), règle SMA150 avec zone de ±3 %, {p.index[0].date()} → {p.index[-1].date()}.", "",
          f"- Part moyenne du satellite en stablecoin : **{in_stable.mean():.0%}** du temps ; entièrement en stablecoin "
          f"{(in_stable > 0.99).mean():.0%} des jours (c'est le cas en ce moment : {in_stable.iloc[-1]:.0%}).",
          f"- Historique Yahoo (clôtures quotidiennes) : USDC au plus bas à {u['USDC-USD'].min():.3f} $, USDT à {u['USDT-USD'].min():.3f} $. "
          "En séance, USDC est tombé à environ 0,87 $ en mars 2023 (faillite de la Silicon Valley Bank), avant de revenir à 1 $ en 3 jours.", "",
          "| Perte de parité | Perte sur le satellite (s'il est 100 % en stablecoin) | Perte sur le portefeuille total | Exemple réel |",
          "|---|---|---|---|"]
    for d, ex in ((0.03, "USDC, clôture de mars 2023"), (0.10, "USDC en séance, mars 2023"), (0.30, "—"),
                  (1.00, "TerraUSD (UST), mai 2022 : stablecoin « algorithmique », non conforme MiCA")):
        md.append(f"| −{d:.0%} | −{d:.0%} | **−{0.30 * d:.1%}** | {ex} |")
    md += ["", "Avec 2 stablecoins différents à parts égales (USDC + EURC, deux émetteurs régulés) et la défaillance d'UN seul :",
           f"perte totale de parité = **−{0.30 * 0.5:.0%}** du portefeuille au lieu de −30 %."]
    out = "\n".join(md) + "\n"
    (Path(__file__).parent / "training_stablecoin_results.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
