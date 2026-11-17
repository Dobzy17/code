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

**Proposition du 14/11 (retirée le 15/11, voir leçon 13) :** passer le satellite à BTC seul.

## 15 novembre 2026 — BTC seul ou BTC+ETH, et test glissant (`training_sleeve_results.md`)

Portefeuille complet testé (70 % ACWI + 30 % crypto avec tendance), frais 0,20 %.

13. **Retirer ETH ne change presque rien : je retire ma proposition d'hier.**
    Depuis 2021 : Sharpe 0,99 avec BTC seul, contre 1,04 avec BTC+ETH ; même perte max (≈ −28 %).
    BTC seul ne gagne que 5 années sur 9. La leçon 9 opposait BTC à un panier de 20 altcoins ; ETH, lui,
    n'en est pas un, et il apporte un peu de diversification. **Le robot reste tel quel.**
13 bis. Le test fait sur un satellite seul (leçon 9) ne se transpose pas au portefeuille complet : dans le
    portefeuille, l'ETF monde (70 %) écrase les écarts. Il faut toujours tester le portefeuille qu'on détient réellement.
14. **Ré-optimiser le réglage chaque année n'aide pas, et c'est même parfois pire.** Test glissant 2021+ :
    BTC seul passe d'un Sharpe de 0,99 (fixe SMA150) à 0,85 (réglage ré-choisi chaque année), avec une perte max de −39 % au lieu de −29 % ;
    pour BTC+ETH, c'est identique (1,05 contre 1,04). Le « meilleur réglage du passé » change presque chaque année
    (SMA50, 150 ou 200). **Règle retenue : on garde SMA150 fixe, on ne ré-optimise jamais sur les résultats récents.**
15. **La première semaine réelle correspond exactement au calcul.** −0,73 % = baisse d'ACWI (−0,84 % × 70 %)
    + frais d'achat (0,14 %). Le robot fait ce que le modèle dit.

## 16 novembre 2026 — fiabilité des données (`training_datacheck_results.md`)

16. **Sur BTC et ETH, les cours Yahoo sont fiables.** Comparés à Kraken sur 719 jours : écart médian de 0,02 %,
    écart max de 0,5 %, aucun jour au-delà de 1 %, et **0 décision différente** du robot sur 570 jours.
    Contre Binance (en USDT) : 1 seule décision différente sur 849 jours. Les erreurs de la leçon 12 touchent
    les petites cryptos, pas BTC ni ETH.
17. **Le vrai problème, c'est l'heure, pas la qualité.** À 3h13, Yahoo n'a pas encore la clôture de la veille,
    mais donne déjà le cours du jour en cours (vieux de 2 h). Le robot décide donc sur un cours
    intrajournalier, alors que le backtest décide sur des clôtures. Avec l'écart actuel (BTC 11 % sous sa moyenne),
    ça ne change rien. Mais un jour où le cours est tout près de la moyenne, la décision pourrait différer du backtest.

**Proposition (non appliquée, en attente de ton accord) :** pour la crypto, le robot prendrait les clôtures
**Kraken** (bougies terminées) au lieu de Yahoo, avec Yahoo en secours. C'est cohérent avec le passage au réel,
puisque Kraken sera la plateforme d'exécution. Les règles de la stratégie ne changent pas, seulement la source des cours.

## 17 novembre 2026 — faux signaux en marché sans tendance (`training_whipsaw_results.md`)

18. **La règle perd sur environ 2 trades sur 3, et c'est normal.** BTC : 10 gagnants sur 33 trades depuis mi-2018.
    ETH : 13 sur 34. Mais un gagnant moyen rapporte +72 % (BTC) ou +110 % (ETH), alors qu'un perdant moyen ne coûte que −5 à −7 %.
19. **Tout le profit vient de quelques grandes tendances.** Les 3 meilleurs trades multiplient le capital
    par 22 (BTC) ou 32 (ETH) ; tous les autres trades ensemble font PERDRE (×0,74 et ×0,64).
    Conséquence pratique : **ne jamais couper la règle après une série de pertes**, sinon on rate le trade
    qui paie tout. C'est la principale cause d'échec des humains avec ce type de stratégie.
20. **Les faux signaux coûtent cher en marché sans tendance.** Trades de moins de 30 jours : 22 pour BTC
    (19 perdants, coût cumulé −55 %) et 21 pour ETH (−59 %). 2025-2026 sont typiques : BTC a fait 10 trades
    en 2025-26, dont 8 faux signaux, pour un résultat de 0 % (2025) puis −15 % (2026).
21. **Yahoo est parfois en retard d'un jour de bourse entier** (clôture ACWI du lundi 16/11 absente le mardi à 3h13,
    même en téléchargement séparé). Ça confirme la condition 6 : il faut une source fiable à l'heure d'exécution.

## À tester ensuite
- Réduire les faux signaux avec une zone tampon : acheter seulement si le cours dépasse la moyenne de X %, vendre seulement
  s'il passe X % en dessous, avec X = 0, 1, 2, 3, 5 %. On ne retient X que si TOUTE la plage améliore le résultat
  (pas de choix du meilleur X), et on vérifie avant et après 2021. Sert aussi à mesurer la zone fragile de la leçon 17.
- Scénario catastrophe : le stablecoin de refuge (USDC) perd sa parité de 10 % pendant que le robot est en cash : impact sur le portefeuille ?
