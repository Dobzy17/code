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

## À tester ensuite

### Bourse (actions, ETF)
- Momentum sectoriel : chaque mois, détenir les 3 ETF sectoriels US (XLK, XLF, XLE, XLV…) les plus forts sur 6 à 12 mois.
  Est-ce que ça bat le S&P 500 après frais, avant et après 2016 ?
- Facteurs « reconnus » via ETF : momentum (MTUM), qualité (QUAL), faible volatilité (USMV), value (VLUE), petites capitalisations (IWM)
  contre le marché (SPY). Lesquels ont tenu leurs promesses depuis leur lancement ?
- Dérive après résultats (PEAD) : les actions qui battent fortement les attentes continuent-elles à monter les semaines suivantes ?
  Utiliser le skill `pead-screener` du dépôt si la clé FMP gratuite le permet, sinon les données Yahoo.
- Dividendes en croissance (skill `dividend-growth-pullback-screener`) contre un ETF dividendes (SCHD, VIG) : gagne-t-on quelque chose à choisir soi-même ?
- Saisonnalité (« Sell in May », effet de fin de mois) : réel ou disparu depuis sa publication ?

### Autres marchés
- Or et matières premières : l'or protège-t-il vraiment un portefeuille en crise (2008, 2020, 2022) ? Quel poids optimal sans regarder le futur ?
- Devises : le « carry trade » (pays à taux élevés contre pays à taux bas) via ETF ou paires de change de Yahoo : rentable pour un particulier ?
- Options : vendre des calls couverts (ETF de type QYLD, JEPI) contre détenir l'indice : le revenu compense-t-il la hausse perdue ?

### Informations hors marché (données alternatives)
Règle : une information ne sert que si elle était CONNUE à la date de la décision (dates de publication réelles,
pas les dates des chiffres révisés) et si elle améliore un test hors échantillon. Sinon, c'est du bruit déjà dans les prix.
- Courbe des taux US (10 ans moins 2 ans, FRED T10Y2Y) : son inversion annonce-t-elle les baisses de la bourse,
  et à quel délai ? Réduire les actions après une inversion aurait-il aidé ou coûté ?
- Indicateur de récession par le chômage (règle de Sahm, FRED SAHMREALTIME, publiée en temps réel) : signal utile pour le cœur actions ?
- Conditions financières et stress (FRED NFCI, spreads de crédit BAMLH0A0HYM2) : le stress du crédit précède-t-il les krachs ?
- Positions des gros spéculateurs (rapport CFTC COT, skill `cot-contrarian-detector`) : des positions extrêmes annoncent-elles
  des retournements sur l'or, le pétrole, le S&P 500, le bitcoin ?
- Moral des investisseurs (indice Peur et Avidité crypto, api.alternative.me) : acheter la peur extrême bat-il la règle de tendance ?
- Activité réelle de Bitcoin (transactions, frais, hashrate via blockchain.info et mempool.space) : est-ce qu'elle précède le prix ?
- Taux de la BCE et inflation en zone euro : effet sur l'euro/dollar et sur la valeur en euros du portefeuille.
- Calendrier : réunions de la Fed et de la BCE, publications d'inflation (skill `economic-calendar-fetcher`) : volatilité
  anormale ces jours-là ? Faut-il éviter de passer des ordres juste avant ?

### Crypto
- Simulation après impôts : PEA contre compte-titres pour le cœur, et effet du report d'impôt via stablecoin pour la crypto.
- Scénario catastrophe : le stablecoin de refuge (USDC) perd sa parité de 10 % pendant que le robot est en cash : impact sur le portefeuille ?
