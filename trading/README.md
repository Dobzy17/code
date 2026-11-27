# Robot de trading (argent fictif)

Tout est gratuit et open source : données Yahoo Finance via `yfinance`, calculs avec `pandas`.

| Fichier | Rôle |
|---|---|
| `research.py` | Teste les stratégies sur le passé, avec frais, et sur une période « hors échantillon » (2021+) qui n'a servi à choisir aucun réglage. Résultats dans `research_results.txt`. |
| `paper.py` | Le robot : une exécution = une journée. Lit le marché, explique chaque décision, passe les ordres fictifs, écrit `logs/AAAA-MM-JJ.md`. |
| `state/` | Mémoire du robot : `portfolio.json` (positions), `journal.csv` (tous les ordres), `equity.csv` (capital jour par jour). |
| `tests/` | Garantit que le backtest n'utilise jamais les cours du futur et compte bien les frais. |

```bash
pip install -r trading/requirements.txt
python3 trading/research.py      # la recherche
python3 trading/paper.py --dry   # ce que le robot ferait aujourd'hui
python3 trading/paper.py         # exécuter la journée
```

## Ce que la recherche a montré (novembre 2026)

- **Crypto :** le suivi de tendance (n'être investi que si le cours est au-dessus de sa moyenne mobile)
  fonctionne avec **tous** les réglages de 50 à 250 jours, y compris après 2021. Perte max ≈ −50 % au lieu de −76 %.
- **Actions :** aucune règle active ne bat le simple achat-conservation d'un ETF. Le robot n'essaie donc pas.
- **Portefeuille du robot** (70 % ETF monde + 30 % crypto avec tendance) : en 2021+, ≈ +19 %/an avec une perte max de −28 %,
  contre −44 % pour le même 70/30 sans règle.

## Limites honnêtes

- Le passé ne garantit rien. La crypto peut perdre 80 % ; 2018–2026 est une période courte.
- Le backtest suppose des poids constants (rééquilibrage continu, sans frais pour ce rééquilibrage).
- Avant tout argent réel : au moins 3 mois de simulation conformes au backtest, une petite somme, et des plafonds.
