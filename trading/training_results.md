# Résultats d'entraînement

Données 2018-01-01 → 2026-11-13, frais 0,20 % par ordre sauf mention contraire.

## 1. Résultats globaux (avant 2021 = choix / 2021+ = hors échantillon)

| Stratégie | Période | Rendement/an | Perte max | Sharpe |
|---|---|---|---|---|
| A. Achat-conservation BTC+ETH | avant 2021 | +16.5% | -87.9% | 0.61 |
| A. Achat-conservation BTC+ETH | 2021+ | +19.6% | -76.3% | 0.60 |
| B. Robot actuel : SMA150 BTC+ETH | avant 2021 | +61.9% | -53.6% | 1.27 |
| B. Robot actuel : SMA150 BTC+ETH | 2021+ | +30.7% | -49.9% | 0.83 |
| C. Donchian ensemble BTC+ETH | avant 2021 | +49.5% | -29.7% | 1.38 |
| C. Donchian ensemble BTC+ETH | 2021+ | +22.6% | -34.4% | 0.79 |
| D. Donchian + volatilité cible BTC+ETH | avant 2021 | +20.9% | -9.5% | 1.61 |
| D. Donchian + volatilité cible BTC+ETH | 2021+ | +9.0% | -15.3% | 0.75 |
| E. Donchian + vol. cible, 14 cryptos | avant 2021 | +10.9% | -9.7% | 1.29 |
| E. Donchian + vol. cible, 14 cryptos | 2021+ | +10.8% | -11.3% | 1.14 |

## 2. Année par année (régularité)

| Année | A | B | C | D | E |
|---|---|---|---|---|---|
| 2018 | -77% | -4% | -5% | -1% | -1% |
| 2019 | +40% | +54% | +44% | +20% | +10% |
| 2020 | +395% | +187% | +143% | +48% | +25% |
| 2021 | +199% | +107% | +129% | +29% | +35% |
| 2022 | -65% | -16% | -18% | -8% | -6% |
| 2023 | +123% | +78% | +32% | +19% | +18% |
| 2024 | +83% | +69% | +45% | +24% | +27% |
| 2025 | -6% | -3% | -2% | -3% | -0% |
| 2026 | -28% | -5% | -5% | -3% | -3% |

## 3. Résistance aux frais (rendement/an sur toute la période)

| Stratégie | 0,10 % | 0,20 % | 0,50 % | 1,00 % |
|---|---|---|---|---|
| A. Achat-conservation BTC+ETH | +18.6% | +18.6% | +18.5% | +18.5% |
| B. Robot actuel : SMA150 BTC+ETH | +41.6% | +40.5% | +37.4% | +32.3% |
| C. Donchian ensemble BTC+ETH | +32.3% | +31.1% | +27.5% | +21.8% |
| D. Donchian + volatilité cible BTC+ETH | +13.4% | +12.9% | +11.5% | +9.2% |
| E. Donchian + vol. cible, 14 cryptos | +11.3% | +10.9% | +9.8% | +8.0% |

## 4. Exécution en retard de 2 jours (robot lent, panne…)

| Stratégie | À l'heure | +2 jours |
|---|---|---|
| A. Achat-conservation BTC+ETH | +18.6% | +16.4% |
| B. Robot actuel : SMA150 BTC+ETH | +40.5% | +41.9% |
| C. Donchian ensemble BTC+ETH | +31.1% | +26.2% |
| D. Donchian + volatilité cible BTC+ETH | +12.9% | +11.4% |
| E. Donchian + vol. cible, 14 cryptos | +10.9% | +9.6% |

## 5. Simulation de 2 000 années possibles (blocs de 30 jours tirés du passé)

| Stratégie | Proba de perdre sur 1 an | Rendement médian | 5 % pires années | Perte max médiane | Perte max (5 % pires) |
|---|---|---|---|---|---|
| A. Achat-conservation BTC+ETH | 40% | +20% | -63% | -51% | -78% |
| B. Robot actuel : SMA150 BTC+ETH | 21% | +40% | -32% | -29% | -52% |
| C. Donchian ensemble BTC+ETH | 23% | +29% | -23% | -22% | -38% |
| D. Donchian + volatilité cible BTC+ETH | 20% | +11% | -9% | -9% | -16% |
| E. Donchian + vol. cible, 14 cryptos | 20% | +10% | -7% | -6% | -12% |

_Biais connu : les 14 cryptos sont celles qui existent encore aujourd'hui (biais du survivant) ; la stratégie E est donc probablement surestimée._
