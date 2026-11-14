# Passer à l'argent réel : les conditions

## Feu vert seulement si TOUT est vrai

| # | Condition | État au 14/11/2026 |
|---|---|---|
| 1 | Au moins 3 mois de simulation sans bug ni jour manqué non expliqué | ⏳ jour 3/90 |
| 2 | Les ordres simulés correspondent à ce que le backtest aurait fait les mêmes jours | ⏳ |
| 3 | Les deux leçons « à tester ensuite » qui concernent le risque sont faites (univers sans biais, test glissant) | 🟡 1/2 : univers sans biais fait (14/11) |
| 4 | L'utilisateur a choisi un montant qu'il accepte de voir baisser de 50 % sans paniquer | ❓ à décider |
| 5 | Le coupe-circuit et les plafonds sont codés dans le module réel, et testés | ⏳ |

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
