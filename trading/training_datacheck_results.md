# Fiabilité des données : Yahoo contre Kraken et Binance

Écart = |Yahoo − source| / source, sur la clôture journalière UTC. Binance cote en USDT (pas en dollars) : un petit écart y est normal.

| Actif | Source | Jours comparés | Écart médian | Écart max (date) | Jours > 1 % | Décisions SMA150 différentes |
|---|---|---|---|---|---|---|
| BTC-USD | Kraken | 719 (2024-11-26 → 2026-11-14) | 0.017% | 0.51% (2024-12-05) | 0 | 0 sur 570 |
| BTC-USD | Binance | 998 (2024-02-21 → 2026-11-14) | 0.043% | 0.39% (2025-10-10) | 0 | 1 sur 849 |
| ETH-USD | Kraken | 719 (2024-11-26 → 2026-11-14) | 0.022% | 0.52% (2024-12-05) | 0 | 0 sur 570 |
| ETH-USD | Binance | 998 (2024-02-21 → 2026-11-14) | 0.048% | 0.68% (2024-12-05) | 0 | 0 sur 849 |

## Constat sur les derniers jours (passage de 3h13, Paris)
Au moment du passage, Yahoo **n'a pas encore la bougie terminée de la veille** (15/11 absent) mais fournit
déjà la bougie **en cours** du jour (16/11, vieille de 2 h). Même constat le 13/11 (12/11 absent).
Kraken, lui, a bien la bougie de la veille, terminée.
