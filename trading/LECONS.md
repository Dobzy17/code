# Ce que l'entraînement m'a appris

Mémoire écrite du robot : chaque leçon vient d'un test reproductible (`research.py`, `training.py`).
On ajoute une ligne à chaque nouveau test, on n'efface jamais une leçon qui dérange.

## 13 novembre 2026 — tests de résistance (`training_results.md`)

1. **Le suivi de tendance crypto est réel, mais moins spectaculaire que le backtest le laisse croire.**
   SMA150 : +62 %/an avant 2021, puis seulement +31 %/an après. Il faut s'attendre à ce que l'avenir soit encore
   moins bon que 2021+. Les études récentes observent aussi cette usure (Quantpedia).
2. **Son vrai atout, c'est d'éviter les catastrophes, pas de gagner plus.**
   En 2018 : −4 % au lieu de −77 %. En 2022 : −16 % au lieu de −65 %. En 2026 : −5 % au lieu de −28 %.
   Dans les années de forte hausse, il gagne MOINS que l'achat-conservation (2020 : +187 % contre +395 %).
3. **Plusieurs signaux combinés (Donchian) divisent les pertes, sans améliorer le rendement ajusté du risque.**
   Perte max 2021+ : −34 % au lieu de −50 %, mais Sharpe 0,79 contre 0,83. Pas de raison de changer le robot pour ça.
4. **Ajuster la taille à la volatilité, c'est un réglage de risque, pas une source de profit.**
   Pertes max ÷ 3, rendement ÷ 3. C'est utile pour l'argent réel : on choisit la perte qu'on peut supporter.
5. **Diversifier sur 14 cryptos** donne le meilleur Sharpe (1,14 après 2021), mais ces 14 cryptos sont celles qui ont
   survécu jusqu'à aujourd'hui (biais du survivant). Je ne m'y fie pas tant que je n'ai pas testé un univers sans ce biais.
6. **Les frais comptent peu à ce rythme** (SMA150 : +40,5 % → +37,4 % avec des frais de 0,5 %),
   **et un retard de 2 jours aussi.** La stratégie est donc exécutable par un robot qui tourne une fois par nuit.
7. **Même la meilleure version perd de l'argent environ 1 année sur 5** (simulation de 2 000 années possibles).
   Une année négative ne prouvera pas que la stratégie est cassée.

## À tester ensuite
- Un univers crypto sans biais du survivant (inclure les cryptos mortes, comme LUNA ou FTT).
- Un test glissant : choisir les réglages sur 3 ans, tester sur l'année suivante, et recommencer chaque année.
- Le comportement en marché sans tendance (2025-2026 : toutes les stratégies légèrement négatives).
