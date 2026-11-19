# Passer à l'argent réel : les conditions

> **Règle absolue (18/11/2026) : AUCUN argent réel tant que l'utilisateur n'a pas dit explicitement « c'est bon ».**
> Même si toutes les conditions ci-dessous sont remplies. D'ici là : entraînement uniquement. Le dépôt ne contient
> aucun code capable d'envoyer un ordre.

## Feu vert seulement si TOUT est vrai

| # | Condition | État au 19/11/2026 |
|---|---|---|
| 1 | Au moins 3 mois de simulation sans bug ni jour manqué non expliqué | ⏳ jour 8/90 |
| 2 | Les ordres simulés correspondent à ce que le backtest aurait fait les mêmes jours | 🟢 semaine 1 conforme (écart 0,00 %) ; à revérifier chaque dimanche |
| 3 | Les deux leçons « à tester ensuite » qui concernent le risque sont faites (univers sans biais, test glissant) | ✅ univers sans biais (14/11) + test glissant (15/11) |
| 4 | L'utilisateur a choisi un montant qu'il accepte de voir baisser de 50 % sans paniquer | 🟢 par défaut : pilote de 500 € (18/11), modifiable |
| 5 | Le coupe-circuit et les plafonds sont codés dans le module réel, et testés | 🟢 codés et testés en mode proposition (`live/`, 6 tests, 17/11) ; reste à les relire avant le premier euro |
| 6 | Source de cours fiable à l'heure d'exécution (bougie terminée) | 🟡 Yahoo fiable sur la valeur, pas sur l'heure ; ✅ robot fictif et module réel sur clôtures Kraken terminées, Yahoo en secours (18/11) |

Date la plus proche réaliste : **mi-février 2027**.

## Le montage concret (France)

**Cœur (70 %) : ETF monde dans un PEA**
- Le PEA est l'enveloppe fiscale la plus avantageuse : après 5 ans, plus d'impôt sur le revenu,
  seulement les prélèvements sociaux.
- ETF MSCI World ou ACWI éligibles PEA (versions « swap » d'Amundi, iShares, BNP…), achetés une fois par mois.
- **Aucun robot nécessaire** : un virement et un ordre mensuels, ou un plan d'investissement programmé.
  Les tests montrent qu'aucune règle active ne fait mieux sur les actions.
- Courtiers : il en existe des dizaines (Boursorama, Fortuneo, Bourse Direct, Trade Republic, Saxo, XTB…).
  Choisir sur les frais et sur le fait d'**ouvrir un PEA en France** (certains n'en proposent pas).

**Satellite (30 % maximum) : BTC + ETH avec la règle de tendance, sur Kraken**
- Kraken est **agréé MiCA** (Central Bank of Ireland, passeport européen) et figure sur la liste blanche de l'AMF.
  Son API est gratuite, et la bibliothèque open source `ccxt` la gère déjà.
- Frais : à vérifier sur la grille officielle de Kraken. Les sites tiers annoncent de 0,16 % à 0,80 % selon l'interface,
  et le robot doit passer par Kraken Pro ou l'API, pas par l'achat simple, plus cher.
- **Astuce fiscale légale :** en France, un échange de crypto contre une autre crypto (y compris un stablecoin)
  n'est **pas imposable** : seule la conversion en euros l'est. Quand la tendance se retourne, le robot
  vend donc en **USDC ou EURC** (stablecoins conformes MiCA), pas en euros. L'impôt est reporté jusqu'au retrait.
  Il reste un risque, faible mais réel, que le stablecoin perde sa parité.
- Sécurité : clé API **sans droit de retrait** et limitée à l'adresse IP du serveur. L'argent ne peut alors
  que s'échanger, jamais sortir du compte.

## Fiscalité à prévoir (à vérifier sur impots.gouv.fr)
- Plus-values crypto converties en euros : flat tax de **30 % ou 31,4 %** selon les sources pour 2026
  (hausse de la CSG votée dans la LFSS 2026 ; les sources se contredisent). Exonération si le total des cessions
  de l'année est inférieur à 305 €.
- Déclarer chaque année : formulaire **2086** (plus-values), **2042-C**, **3916-bis** (compte crypto à l'étranger,
  amende si oubli). Depuis 2026, les plateformes transmettent aussi les données au fisc (DAC8).

## Garde-fous du module réel (à coder avant le premier euro)
1. Montant maximal par ordre et par jour, codé en dur.
2. Coupe-circuit : −35 % depuis le plus haut → arrêt total ; seul un humain peut relancer.
3. Le robot refuse d'agir si les données ont plus de 48 h ou si un cours bouge de plus de 40 % en un jour
   (donnée probablement erronée).
4. Mode « proposition » le premier mois : le robot prépare les ordres, l'utilisateur valide d'un clic.
5. Journal de chaque ordre réel, rapproché chaque semaine du relevé Kraken.

## Montant : pilote par défaut (18/11/2026, l'utilisateur a dit « fais au mieux »)

Claude ne connaît pas la situation financière de l'utilisateur : ce montant est un **défaut prudent**, pas un conseil personnalisé.

**Avant le premier euro, trois conditions de bon sens :**
1. Une épargne de précaution de 3 à 6 mois de dépenses existe déjà, sur un livret, et on n'y touche pas.
2. Pas de dette à taux élevé en cours (crédit à la consommation, découvert) : la rembourser rapporte plus, et c'est sans risque.
3. Jamais d'argent emprunté, ni d'argent prévu pour le loyer, les factures ou un projet proche.

**Phase pilote, 3 mois après le feu vert :**
- **500 € au total**, répartis comme le robot : 350 € en ETF monde dans un PEA, 150 € en BTC/ETH sur Kraken avec la règle de tendance.
  Une baisse de 50 % coûterait 250 €. L'objectif n'est pas de gagner, mais de vérifier que tout fonctionne avec de l'argent réel
  (ordres, frais, déclarations).
- Plafonds du module réel : 250 € par ordre, 500 € par jour.
- Mode proposition : le robot propose, l'utilisateur valide chaque ordre à la main.

**Ensuite, seulement si le pilote est conforme au modèle :**
- Ajouter une somme mensuelle fixe que l'utilisateur ne regrettera pas (par exemple 50 à 100 €/mois).
  Investir régulièrement réduit le risque de tout investir au plus haut.
- Garder la crypto à 30 % au maximum de l'ensemble, et rééquilibrer une fois par an.
- Relever les plafonds en proportion, jamais pour « rattraper » une perte.
