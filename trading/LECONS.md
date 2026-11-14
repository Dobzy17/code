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

## 14 novembre 2026 — sans biais du survivant (`training_survivor_results.md`)

Paniers = les ~20 premières cryptos AU DÉBUT de la période (début 2018 : 15 sur 19 sont en perte
aujourd'hui ; début 2021 : 12 sur 20), y compris celles qui ont disparu.

8. **Le suivi de tendance NE protège PAS un panier d'altcoins avec une simple moyenne mobile.**
   Panier 2018 + SMA150 : +3,8 %/an, perte max −81 %. C'est pire que de garder BTC seul (+19,9 %/an).
   Les altcoins meurent lentement et la moyenne mobile se fait piéger à chaque faux rebond.
9. **Le meilleur résultat, c'est BTC seul avec la tendance, et c'est stable sur les deux départs :**
   +33,2 %/an (perte max −57 %) depuis 2018, et +25,1 %/an (perte max −45 %) depuis 2021.
10. **La leçon 5 était bien gonflée par le biais du survivant.** « Donchian + volatilité cible, 14 cryptos » :
    Sharpe 1,14 avec les survivants, contre 0,83 (2018) et 0,92 (2021) avec les vrais paniers.
    Ça reste correct (pertes max d'environ −13 %), mais ce n'est pas meilleur que BTC seul.
11. **Les cassures combinées (Donchian) résistent bien mieux que la moyenne mobile sur les altcoins**
    (panier 2018 : +16,7 %/an contre +3,8 %/an). Si un jour on trade des altcoins, ce sera avec cette méthode, jamais avec la SMA.
12. **Les données gratuites de Yahoo contiennent de fausses valeurs** (BTG, ICX : bonds de +300 à +3 000 % en un jour
    qui retombent le lendemain). Ces erreurs avaient multiplié par 12 un backtest. Elles sont maintenant neutralisées
    (`clean_spikes`, test unitaire ajouté). Ce nettoyage prudent efface aussi quelques vrais bonds (DOGE en janvier 2021) :
    les paniers 2021 sont donc légèrement sous-estimés.

**Proposition (non appliquée, en attente de ton accord) :** faire passer le satellite crypto du robot de BTC+ETH à
BTC seul, ou à BTC majoritaire. À confirmer d'abord par le test ci-dessous.

## À tester ensuite
- BTC seul contre BTC+ETH dans le satellite du robot (même période, mêmes frais, test glissant) : faut-il garder ETH ?
- Vérifier les cours Yahoo avec une deuxième source (Kraken ou Binance) avant tout argent réel : écart quotidien sur BTC et ETH.
- Un test glissant : choisir les réglages sur 3 ans, tester sur l'année suivante, et recommencer chaque année.
- Le comportement en marché sans tendance (2025-2026 : toutes les stratégies légèrement négatives).
