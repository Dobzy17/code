# Ce que l'entraînement m'a appris

**Objectif : le PROFIT.** Chaque test est jugé sur une question : combien d'argent en plus, après frais et impôts,
par rapport à l'ETF monde seul, et avec quel risque de grosse perte ? Une idée qui ne rapporte pas plus est écartée,
même si elle est séduisante.

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

**ACCEPTÉ le 18/11/2026, en production :** pour la crypto, le robot prend les clôtures
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

## 17 novembre 2026 (journée, à la demande) — zone tampon, multi-actifs, module réel

22. **Une zone tampon ne rapporte pas plus, mais elle divise les ordres par deux.** Avec une zone de 0 à 5 %, le Sharpe reste
    entre 1,00 et 1,04 après 2021 (à chaque fois, aucune amélioration de rendement), mais le nombre d'ordres crypto passe de 136
    (sans zone) à 70 (zone de 2 %) puis 48 (zone de 5 %). Avec la zone de 3 %, la perte max passe de −28,0 % à −25,8 %.
    **Zone de 3 % : ACCEPTÉE le 18/11/2026, en production dans paper.py et live/propose.py**. C'est moins d'ordres, donc moins de frais réels, moins de lignes
    à déclarer, et moins de sensibilité à l'heure du cours (le cours n'est à moins de 2 % de sa moyenne
    que 4 à 5 % des jours).
23. **Le suivi de tendance « des fonds pros », version particulier (8 ETF, achat seulement), ne vaut pas le coup.**
    Depuis 2016 : +3 à +4 %/an (Sharpe 0,48 à 0,60), contre +9,4 %/an (Sharpe 0,90) pour un simple 60/40.
    Il protège en crise (2008 : −1 à −7 % au lieu de −17 % ; 2022 : −6 % au lieu de −16 %), mais il rate trop de hausse.
    L'avantage documenté par les études vient des contrats à terme, de la vente à découvert et de plus de 50 marchés,
    ce qu'un particulier ne reproduit pas avec 8 ETF. **Le cœur du robot reste sans règle.**
    Limite du test : le cash est compté à 0 %, alors qu'il rapporte environ 3-4 % depuis 2023. Ça défavorise un peu les versions avec tendance.
24. **En passant : le 60/40 a battu 100 % ACWI en rendement ajusté du risque** (Sharpe 0,90 contre 0,75 depuis 2016 ;
    perte max −21 % contre −34 %). Si tu crains les fortes baisses, une part d'obligations dans le cœur est une option
    simple. C'est une question de goût du risque, à toi de choisir.
25. **Le module argent réel existe, en mode proposition** (`live/propose.py`). Il prend les clôtures Kraken terminées
    (la bougie de la veille est bien là à l'heure du robot, contrairement à Yahoo) et applique 5 garde-fous testés :
    données trop vieilles, mouvement suspect de plus de 40 %, historique trop court, coupe-circuit, plafonds de 500 € par ordre et 1 000 € par jour.
    Il ne contient **aucun code d'envoi d'ordre** : il écrit une proposition à valider à la main.

## 18 novembre 2026 — rendement du cash (`training_cash_results.md`)

26. **Rémunérer le cash améliore un peu les stratégies avec tendance, mais ne change aucune conclusion.**
    Taux des bons du Trésor US à 3 mois : 0,2 % (2008-2015), 0,9 % (2016-2021), 4,0 % (2022+).
    Robot 70/30 : +18,9 % → +19,4 %/an depuis 2021 (+0,5 point). Crypto seule SMA150 : +30,6 % → +32,5 % (+1,9 point).
    8 ETF avec tendance : +3,6 % → +4,4 à +4,5 %, toujours loin du 60/40 (+9,4 %). **La leçon 23 tient.**
27. **En pratique, ce gain ne s'obtient pas gratuitement.** Le refuge prévu pour la crypto, c'est le stablecoin, qui ne rapporte
    rien par défaut. Pour toucher un taux, il faudrait passer en euros (fonds monétaire), et cette vente est imposable (leçon fiscale
    de PASSAGE_ARGENT_REEL.md). De plus, les taux en euros sont différents des taux US utilisés ici. Pour +0,5 point par an, ça ne vaut pas
    de déclencher l'impôt à chaque signal. **On garde le stablecoin.** À revoir seulement si une rémunération sûre
    et conforme MiCA du stablecoin existe (non vérifié).
28. **Le contrôle croisé tourne chaque nuit** : le robot fictif (Yahoo, USD) et la proposition réelle (Kraken, EUR)
    sont d'accord le 17 et le 18/11 (BTC et ETH sous leur moyenne). Tout désaccord sera signalé.

## 19 novembre 2026 — nuit (rotation sectorielle, peur extrême, incidents)

29. **Bourse — choisir les secteurs « qui montent » ne bat pas l'indice.** 9 ETF sectoriels, top 3 par momentum,
    1999-2026, frais 0,20 % : après 2013, entre +11,0 % et +13,6 %/an selon la durée (3 à 12 mois), contre **+14,2 % pour le S&P 500**
    (Sharpe 0,71 à 0,84 contre 0,88). Avant 2013, quelques versions font un peu mieux que l'indice, mais aucune ne bat les
    9 secteurs à poids égaux (+5,6 %/an). Le seul gain stable, c'est une perte max un peu plus faible (−45 % contre −55 %).
    **Pas d'intérêt pour le robot.**
30. **Hors marché — « acheter la peur extrême » est un mythe sur la crypto.** Depuis 2018, 180 jours après une peur extrême (≤ 15/100),
    BTC a fait en médiane **+3 %, contre +13 % pour un jour quelconque**. Sur 16 épisodes terminés, 9 ont fini en baisse
    (2018, 2022 : −40 à −51 %). La stratégie « acheter et garder 180 jours après chaque peur extrême » fait **−5,7 %/an**
    (Sharpe 0,16), contre +41,6 %/an pour la règle de tendance du robot. Combiner les deux dégrade la tendance (Sharpe 1,04 → 0,66).
    Aujourd'hui, l'indice est à 10/100 : c'est une information sur le moral, **pas un signal d'achat**. La peur extrême accompagne
    souvent une tendance baissière qui continue. Curiosité : l'avidité extrême (≥ 80) a été suivie de +26 % à 90 jours (médiane) ;
    c'est la tendance qui parle, pas un signal de vente.
31. **Opérationnel — 6 incidents répétés et testés** (`live/PROCEDURE_INCIDENTS.md`, `tests/test_incidents.py`) :
    Kraken en panne, historique trop court, données trop vieilles, coupe-circuit, ordre exécuté à moitié. Un défaut a été trouvé
    et corrigé : si Kraken ne répondait pas, le module réel **plantait** sans message. Désormais, il écrit « AUCUN ORDRE »
    avec la raison, et il n'utilise volontairement **aucune source de secours** avec de l'argent réel. Un ordre exécuté à moitié est complété
    sans doublon à la proposition suivante.
32. **Veille installée** (`veille.py`, chaque nuit) : courbe des taux, règle de Sahm, conditions financières, prime de risque,
    taux BCE, positions CFTC (or, pétrole, S&P 500, bitcoin), Peur et Avidité, activité de la blockchain Bitcoin.
    Comparaison quotidienne avec les références : `compare.py` → `state/comparaison.csv`.

## 20 novembre 2026 — nuit (facteurs, or, impôts)

33. **Bourse — les « facteurs » en ETF n'ont pas battu le S&P 500.** Depuis le lancement de chaque ETF :
    momentum +0,3 point par an (bruit), qualité −0,3 point, value −1,4 point, faible volatilité −3,0 points, petites capitalisations −3,2 points.
    Aucun ne gagne nettement plus d'une année sur deux. La « faible volatilité » ne réduit même pas la pire baisse
    (−33 % contre −34 %). Leur corrélation avec SPY est de 0,86 à 0,98 : ce sont presque des copies de l'indice, avec des frais en plus.
    **Le cœur reste un ETF monde simple.**
34. **Autres marchés — l'or protège dans les krachs LENTS, pas dans les krachs rapides.** Krachs de plus de 15 % du S&P 500 depuis 2004 :
    2008-09 : or +24 % (S&P −55 %) ; 2018 : +5 % ; 2025 : +2 %. Mais 2020 (Covid) : −4 %, et 2022 : −7 %. Les obligations
    ont fait mieux en 2020 (+6 %) et bien pire en 2022 (−15 %) : aucun refuge ne marche à tous les coups.
    Ajouter de l'or améliore le portefeuille de façon **régulière sur toute la plage** (0 à 30 %) et sur les deux périodes :
    en 2016+, la perte max passe de −34 % (0 % d'or) à −31 % (10 %) puis −28 % (20 %), à rendement presque identique (+14,4 % → +14,3 %).
    **Limite importante :** 2005-2026 a été une période très favorable à l'or (deux grandes hausses). De plus, la corrélation
    or/actions est aujourd'hui élevée (+0,36 contre +0,07 en médiane) : il protège moins en ce moment.
    **Proposition (en attente de ton accord) : 10 % d'or dans le cœur** (60 % ACWI + 10 % or + 30 % crypto). **Attention fiscale :**
    l'or (ETC) n'est PAS éligible au PEA : il irait sur un compte-titres, imposé à 30 %.
35. **Crypto — vendre en stablecoin plutôt qu'en euros vaut environ +25 % de capital final.** Satellite BTC/ETH avec la règle de tendance,
    2018 → 2026, 10 000 au départ, impôt de 30 % : **123 475** net avec la vente en stablecoin (un seul impôt au retrait)
    contre **99 020** avec la vente en euros à chaque signal (impôt chaque année ; −20 %). Avec un taux de 31,4 % : 121 205 contre 96 115.
    Les impôts payés sont presque les mêmes. La différence vient des intérêts composés sur l'impôt reporté.
    **Le choix du stablecoin est confirmé**, sous réserve du risque de perte de parité (prochain test crypto).
36. **PEA contre compte-titres pour le cœur** : avec le même ETF et 10 000 € placés, le PEA laisse +1 483 € de plus après 10 ans
    et +4 686 € après 20 ans (à 8 %/an). **Le cœur actions va dans un PEA, sans hésiter**, à condition d'utiliser un ETF monde éligible.

## 21 novembre 2026 — nuit (radar de tous les marchés, satellite IA, courbe des taux)

37. **Courir après les marchés « qui montent » fait PERDRE de l'argent par rapport à l'ETF monde.** Radar de 45 ETF
    (pays, secteurs, matières premières, obligations, immobilier), top 5 chaque mois par tendance sur 12 mois :
    depuis 2009, ×2,65 contre **×6,30 pour l'ETF monde sans rien faire**. Le résultat est le même avec le top 3 (×3,54), le top 10 (×3,54)
    ou sans règle de sortie (×2,98) : ce n'est pas un problème de réglage. Après impôts, c'est pire : **1 € devient 1,78 € avec
    le radar** (compte-titres, impôt chaque année) **contre 5,39 € avec l'ETF monde dans un PEA**. Les marchés « chauds » (uranium, pétrole,
    Brésil, biotech, argent) se retournent souvent juste après avoir été les plus forts. **Écarté.**
38. **Satellite IA : le résultat sur Nvidia est un mirage du recul.** Depuis 2010, 10 % de Nvidia porte un portefeuille S&P 500
    de +13,5 % à +16,7 %/an, mais c'est parce qu'on SAIT aujourd'hui que Nvidia a gagné. **Le test honnête**, avec les 6 leaders tech
    choisis en mars 2000 (Microsoft, Cisco, Intel, Oracle, IBM, Qualcomm) : 10 % de satellite = +7,9 %/an contre +7,8 % pour le S&P 500
    seul. Le panier entier a fait ×7,6 en 26 ans, avec **−71 %** en chemin, et ce résultat est encore flatté par l'absence de Lucent et Nortel,
    disparus. Pendant 12 ans (2000-2012), le panier a rapporté **0 %**. La règle de tendance n'y change presque rien. **Pas de satellite IA :**
    l'ETF monde contient déjà Nvidia, Microsoft, etc. à leur juste poids, et il remplace automatiquement les perdants.
39. **Hors marché — la courbe des taux inversée annonce bien les récessions, mais elle ne permet PAS d'en profiter.** 7 inversions depuis 1976 :
    le S&P 500 était encore en HAUSSE 12 mois après 5 d'entre elles (+7 % à +31 %). Les krachs arrivent parfois plus de 2 ans après
    (2005 → krach de 2008). Sortir des actions pendant l'inversion, ou 6, 12 ou 18 mois après : **aucune version ne réduit la pire baisse (−55 %)**,
    et la plupart rapportent moins (2000+ : de +6,6 % à +8,4 % contre +8,0 %). La courbe est aujourd'hui à +0,29 : aucun signal,
    et de toute façon **elle ne sera pas utilisée par le robot**.

## 22 novembre 2026 — nuit (options, stablecoin, nuits manquées)

40. **Options : les ETF « à gros revenu » (calls couverts) font perdre de l'argent par rapport à l'indice.** QYLD : +7,3 %/an contre
    +17,2 % pour le Nasdaq 100 depuis 2014 (×2,46 contre ×7,68). XYLD : −5,7 points par an. JEPI : −4,7. JEPQ : −4,5. Leur « rendement de 8 à 12 % »
    sert surtout à rendre au client son propre capital, tout en lui faisant rater la hausse. Ils baissent un peu moins dans
    les krachs (QYLD −25 % contre −35 %), mais en France, leur revenu est imposé à 30 % chaque année et ils sont exclus du PEA. **Écarté.**
41. **Crypto : le risque du stablecoin est réel mais limité, et il se réduit facilement.** Le satellite est en stablecoin
    **47 % du temps** (100 % en ce moment). Perte de parité de 10 %, comme USDC en séance en mars 2023 : −3 % sur le portefeuille total.
    Faillite totale, comme TerraUSD en 2022 : −30 %. **Proposition (en attente de ton accord) :** répartir le refuge à parts égales
    entre deux stablecoins conformes MiCA d'émetteurs différents (**USDC + EURC**), ce qui limite le pire cas à −15 % ;
    plus une alerte si l'un d'eux cote sous 0,98.
42. **Opérationnel : les nuits manquées sont maintenant détectées et écrites dans le journal** (`missed_nights`, testé).
    Il n'y a rien à « rattraper » : le robot compare chaque nuit ses positions aux cibles du jour et rééquilibre en une fois.
    Premier rééquilibrage réel observé le 22/11 : achat de 188 $ d'ETF après sa chute (passé sous 68 %), exactement selon la règle.

## 23 novembre 2026 — nuit (radar inversé, stress du crédit, rééquilibrage)

43. **Acheter les marchés les plus faibles des 3 dernières années ne marche pas sur les ETF.** 16 pays, 5 plus faibles : ×3,70 depuis 2009,
    contre ×6,08 pour l'ETF monde. Sur 45 marchés, c'est pire (×1,97 à ×3,05, perte max jusqu'à −75 %). Le rattrapage documenté par la recherche
    joue sur 3 à 5 ans ou plus, avec des actions individuelles : il ne se capture pas ici.
44. **Le cas le plus instructif depuis le début : un résultat « trop beau » démonté.** Garder les 5 marchés les plus FORTS sur 3 ans
    donnait ×8,70 contre ×6,08 pour l'ETF monde. La vérification montre que c'est un hasard de réglage : avec 2 ans de recul, ×3,3 à ×4,1 ;
    avec 4 ans, ×5,2 à ×5,8 (moins bien que l'ETF monde). Et sans SMH, XLK et QQQ, que j'avais mis dans la liste en SACHANT qu'ils avaient gagné,
    on tombe à **×4,07**. **Écarté.** La règle pour la suite : un résultat qui ne tient que pour un seul réglage est un piège.
45. **Hors marché — le stress du crédit réduit les krachs, mais il coûte la moitié du rendement.** Sortir des actions quand l'écart de
    crédit Baa dépasse sa moyenne (100, 200 ou 300 jours) : la pire baisse passe de −55 % à −20 % / −36 %, mais le rendement tombe
    de +17,1 % à +6,5 / +8,5 %/an (1987-1999) et de +7,8 % à +4,6 / +6,3 % (2000+). On reste en cash près de la moitié du temps. **Écarté :**
    moins de profit. (L'historique haut rendement de FRED ne remonte plus qu'à 2024 : trop court pour conclure.)
46. **Rééquilibrage : la fréquence compte peu pour le gain, beaucoup pour le nombre d'ordres.** Portefeuille du robot depuis 2018 :
    seuil de 2 points (actuel) +21,2 %/an et 267 ordres ; **seuil de 5 points +22,3 %/an et 109 ordres** ; mensuel +21,6 % ; annuel +21,1 % ;
    jamais +21,2 %, mais perte max −41 % au lieu de −34 %. Rééquilibrer sert à contrôler le risque, pas à gagner plus.
    **Proposition (en attente de ton accord) : passer le seuil de 2 à 5 points.** Le rendement est équivalent, mais il y a 60 % d'ordres en moins
    (moins de frais réels et de lignes à déclarer). Un bug de simulation (quantité résiduelle après une vente) a été trouvé et corrigé dans le test,
    et vérifié absent du robot.

## 24 novembre 2026 — nuit (saisonnalité, carry trade, répétition générale)

47. **Bourse — la saisonnalité a perdu l'essentiel de sa force depuis sa publication.** Rendement moyen d'un jour de fin de mois :
    +0,136 % en 1950-1986 contre +0,054 % en 2002-2026 (−60 %). Écart novembre-avril / mai-octobre : 5 fois plus faible.
    Les stratégies perdent contre « toujours investi » : « Sell in May » +6,3 %/an contre +9,8 % depuis 2002 ; « fin de mois » −0,8 %/an
    (les frais d'entrée et de sortie mangent tout). **Écarté.** Un effet connu de tous finit par disparaître.
48. **Autres marchés — le carry trade sur devises ne rapporte presque rien et peut faire très mal.** Achat des 2 devises du G10 à taux haut,
    vente des 2 à taux bas, 2006-2026 : **+0,5 %/an**, perte max −37 % (2008 : −29 %), et −0,3 %/an depuis 2013. En plus, il n'est accessible
    au particulier qu'avec des CFD à effet de levier, que l'AMF déconseille. **Écarté.**
49. **Opérationnel — la répétition générale a trouvé un VRAI point bloquant** (`live/PROCEDURE_JOUR_J.md`) : en réalité, il y aura deux comptes
    séparés (PEA et Kraken) qui ne peuvent pas s'échanger d'argent sans casser le PEA (retrait avant 5 ans) ou déclencher l'impôt
    (vente de crypto en euros). Le rééquilibrage 70/30 du robot fictif est donc **impossible tel quel**. Solution : rééquilibrer
    uniquement avec les nouveaux versements mensuels. **Proposition (en attente de ton accord) :** adapter le robot fictif pour qu'il
    simule ces deux comptes séparés, afin que le test des 90 jours corresponde à la réalité. Autres points notés : suivi de l'ETF en euros,
    deuxième source pour la clôture d'ACWI (Yahoo a eu 1 jour de retard les 17, 20 et 23/11), formulaire 3916-bis chaque année.

## 25 novembre 2026 — nuit (deux comptes séparés, règle de Sahm, décisions en semaine)

50. **Opérationnel — avec deux comptes séparés, on gagne plus, mais le portefeuille devient surtout de la crypto.**
    De 2017-11 à aujourd'hui, 10 000 au départ, sans versement : un compte unique avec rééquilibrage (robot actuel) donne **53 829**, avec une perte max de −34 % ;
    deux comptes avec rééquilibrage par les seuls versements donnent **74 655**, avec une perte max de −36 %. Mais la part crypto (et stablecoin) dérive
    **jusqu'à 86 %** (77 % aujourd'hui) au lieu de rester vers 30 %. Avec 100 €/mois : 110 157 contre 82 334, et une part crypto qui va jusqu'à 83 %.
    Le gain vient du fait de laisser courir le gagnant (la crypto). La règle de tendance a limité les dégâts, mais c'était un pari
    concentré, et le risque de perte de parité du stablecoin (leçon 41) grandit avec cette part. **À décider : plafonner la part crypto**
    (par exemple à 40-50 %, en vendant l'excédent en euros une fois par an, ce qui est imposable) ou accepter la dérive. Test ajouté à la liste.
51. **Hors marché — la règle de Sahm est le premier signal macro qui réduit vraiment les krachs sans coûter de rendement depuis 2000.**
    Sortir des actions quand l'indicateur du chômage (calculé avec les chiffres de l'époque) atteint 0,50 : perte max **−34 % au lieu de −55 %**
    (elle a évité l'essentiel de 2008), avec un rendement de +8,1 %/an contre +8,0 % depuis 2000, mais +12,3 % contre +14,7 % en 1977-1999.
    Elle déclenche tard (le S&P 500 a souvent déjà perdu 8 à 21 %), et de fausses alertes existent (août 2024 : +23 % les 12 mois suivants).
    **Pas de changement pour l'instant** : il n'y a que 9 signaux en 50 ans, ce qui est trop peu pour s'y fier. Mais elle reste suivie dans la veille, et c'est une candidate
    sérieuse pour protéger le cœur. Bon point : un arbitrage À L'INTÉRIEUR d'un PEA n'est pas imposé.
52. **Crypto — décider en semaine seulement ne change presque rien.** Tous les jours : +32,2 %/an depuis 2021, perte max −53 %, 60 ordres ;
    du lundi au vendredi : +33,3 %, −48 %, 56 ordres ; une fois par semaine : +25,7 %. L'écart en faveur de la semaine est faible et
    probablement dû au hasard. **On garde la décision quotidienne**, mais une fois par semaine coûte cher : ne pas espacer.

## 26 novembre 2026 — nuit (plafond crypto, positions COT, ETF dividendes)

53. **Plafonner la crypto coûte du rendement, mais c'est une assurance que je recommande.** Montage à deux comptes, 2017-11 → aujourd'hui,
    10 000 au départ, net de TOUS les impôts : sans plafond **56 513** (crypto jusqu'à 86 % du total) ; plafond 50 % **52 748** (−7 %) ;
    40 % : 48 415 ; 30 % : 42 497. La perte max est la même partout (−36/−37 %), parce que la règle de tendance protège déjà des krachs de PRIX.
    **Mais elle ne protège pas** d'une faillite de plateforme (FTX, 2022), d'un piratage ou d'une perte de parité du stablecoin (leçon 41) :
    avec 77 % du patrimoine sur Kraken, ce risque devient énorme. **Proposition (en attente de ton accord) : plafond de 50 %**,
    vérifié chaque janvier ; l'excédent est vendu en euros (imposé) et versé sur le PEA. C'est −7 % de gain historique pour diviser par environ 1,5 à 2
    l'exposition à un risque qui ne se voit pas dans les backtests.
54. **Hors marché — les positions extrêmes des spéculateurs (COT) ne donnent pas de signal exploitable.** Depuis 2000 : quand les spéculateurs
    sont massivement acheteurs d'or (> 90/100), l'or a fait MIEUX ensuite (+8,4 % à 26 semaines contre +5,7 %), ce qui est l'inverse
    de la lecture « à contre-courant ». Seul indice cohérent : vente massive sur le S&P 500 (< 10) → +4,3 % à 12 semaines contre +3,0 %
    (76 % de cas positifs contre 68 %), mais il y a peu de cas indépendants. **Gardé comme information de la veille**, pas comme signal.
55. **Bourse — les ETF dividendes ont tous fait moins bien que le S&P 500.** VIG −0,6 point par an, SCHD −1,1, DVY −1,9, HDV −2,4, NOBL −2,7.
    Seul VIG a un peu limité la pire baisse (−47 % contre −55 %). DVY a fait pire (−63 %). En France, ils sont exclus du PEA et leurs dividendes sont imposés
    chaque année : **écartés.** Un dividende n'est pas un « bonus » : c'est une partie de la valeur de l'action qu'on vous verse (et qu'on vous impose).

## À tester ensuite

### Bourse (actions, ETF)
- Actions françaises et européennes en PEA : un ETF CAC 40 ou Europe contre un ETF monde, en euros, sur 20 ans. Faut-il un biais « maison » ?
- Investir une somme d'un coup ou l'étaler sur 6 à 12 mois (DCA) : lequel rapporte le plus, historiquement, et à quel coût de regret ?
- Dérive après résultats (PEAD) : les actions qui battent fortement les attentes continuent-elles à monter les semaines suivantes ?
  Utiliser le skill `pead-screener` du dépôt si la clé FMP gratuite le permet, sinon les données Yahoo.


### Radar de tous les marchés (où est l'argent en ce moment ?)
- Marchés « à fort potentiel » souvent cités (Inde, uranium, cuivre, défense européenne, petites capitalisations) : tester
  chacun avec la règle de tendance, et regarder ce qui s'est passé APRÈS les périodes où ils étaient « à la mode ».

### Autres marchés
- Obligations d'État en euros (Bund, OAT) via ETF : quelle part dans le cœur pour réduire la perte max sans trop coûter (leçon 24) ?
- L'or sur une période défavorable (1980-2001, or en baisse de plus de 60 %) avec des données de long terme : la conclusion de la leçon 34 tient-elle ?

### Informations hors marché (données alternatives)
- Règle de Sahm appliquée au cœur DANS le PEA (arbitrage non imposé) avec l'ETF monde depuis 2008 et le S&P 500 depuis 1976 : confirmer
  la leçon 51 sur un autre indice et chiffrer le nombre d'ordres.
Règle : une information ne sert que si elle était CONNUE à la date de la décision (dates de publication réelles,
pas les dates des chiffres révisés) et si elle améliore un test hors échantillon. Sinon, c'est du bruit déjà dans les prix.
- Activité réelle de Bitcoin (transactions, frais, hashrate via blockchain.info et mempool.space) : est-ce qu'elle précède le prix ?
- Taux de la BCE et inflation en zone euro : effet sur l'euro/dollar et sur la valeur en euros du portefeuille.
- Calendrier : réunions de la Fed et de la BCE, publications d'inflation (skill `economic-calendar-fetcher`) : volatilité
  anormale ces jours-là ? Faut-il éviter de passer des ordres juste avant ?

### Être opérationnel le jour du feu vert
- Deuxième source pour la clôture quotidienne de l'ETF monde (ou de l'ETF PEA en euros), pour éviter le retard de Yahoo.
- Préparer la déclaration fiscale de fin d'année à partir du journal (formulaires 2086 et 3916-bis), sur les trades fictifs.

### Crypto
- Actif crypto supplémentaire dans le satellite (SOL, par exemple), mais seulement avec un univers choisi à l'époque (leçon 10) :
  améliore-t-il BTC+ETH avec la règle de tendance, ou est-ce encore du biais du survivant ?
