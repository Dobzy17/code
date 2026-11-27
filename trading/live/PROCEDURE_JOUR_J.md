# Répétition générale : le premier jour en argent réel (24/11/2026)

> Rien de tout ceci ne se fait avant que l'utilisateur dise explicitement « c'est bon ».

## ⛔ Point bloquant trouvé pendant la répétition : deux comptes séparés

Le robot fictif traite le portefeuille comme **un seul compte** : il peut vendre de la crypto pour racheter l'ETF (rééquilibrage 70/30).
En réalité, il y aura **deux comptes qui ne communiquent pas** :
- le **PEA** (ETF monde) : l'argent ne peut pas en sortir pour aller sur Kraken. Un retrait avant 5 ans **clôture le PEA** ;
- le **compte Kraken** (crypto + stablecoin) : sortir de l'argent vers la banque = vente en euros = **impôt** (leçon 35).

**Conséquence : on ne rééquilibre JAMAIS en déplaçant de l'argent entre les deux comptes.** On rééquilibre seulement avec
les **nouveaux versements** : chaque mois, le versement va vers le compte qui est sous sa cible (70 % / 30 %).
La leçon 46 montre que le rééquilibrage sert à limiter le risque et rapporte peu : la perte max passerait de −34 % à environ −41 %
sans rééquilibrage, ce qui est acceptable pour un essai de 500 €. **À intégrer au robot fictif avant le feu vert (proposition).**

## Déroulé du premier jour (essai de 500 €)

| Étape | Qui | Durée estimée | Points à vérifier |
|---|---|---|---|
| 1. Ouvrir un PEA chez un courtier en ligne | Utilisateur | 1 à 3 semaines (pièces d'identité, justificatif) | Frais de courtage par ordre de 350 € ; courtier qui ouvre bien un PEA en France |
| 2. Choisir l'ETF monde | Claude propose, l'utilisateur valide | — | Mention « éligible PEA » sur la fiche ; capitalisant ; frais annuels bas ; indice MSCI World ou ACWI |
| 3. Virer 350 € et passer l'ordre d'achat | Utilisateur | 1 à 3 jours | Ordre à cours limité (pas « au marché ») pendant les heures d'ouverture |
| 4. Ouvrir un compte Kraken (vérification d'identité) | Utilisateur | Quelques jours | Kraken agréé MiCA, présent sur la liste blanche de l'AMF (leçon PASSAGE) |
| 5. Virer 150 € par virement SEPA | Utilisateur | 1 à 2 jours | Frais de dépôt SEPA (grille officielle Kraken) |
| 6. Créer une clé API **en lecture seule** (aucun droit de trading ni de retrait) | Utilisateur | 10 min | Plus tard seulement, éventuellement, le droit de trader ; **jamais** le droit de retrait |
| 7. Remplir `live/holdings.json` (euros, BTC, ETH, plus haut, coupe-circuit) | Claude | 5 min | Fichier ignoré par git (données personnelles) |
| 8. Lancer `live/propose.py` et lire la proposition | Claude | 1 min | Si BTC/ETH sont sous leur moyenne (comme aujourd'hui) : on garde les 150 € en **EURC/USDC**, on n'achète rien |
| 9. Valider à la main chaque ordre sur Kraken Pro | Utilisateur | 5 min | Ordre limité, montant ≤ 250 € ; on note l'exécution réelle |
| 10. Mettre à jour `holdings.json` avec l'exécution RÉELLE | Claude | 5 min | Ordre partiel : la proposition suivante complète (test d'incident) |
| 11. Rapprochement hebdomadaire : relevé Kraken et relevé du courtier contre le journal | Claude + utilisateur | 10 min/semaine | Écart nul attendu |

## Obligations fiscales à ne pas oublier
- **Formulaire 3916-bis** : déclarer CHAQUE année le compte Kraken (compte d'actifs numériques à l'étranger), même sans vente. Amende si oubli.
- **Formulaire 2086** : seulement les années où l'on vend de la crypto contre des euros (pas pour les échanges crypto ↔ stablecoin).
- PEA : rien à déclarer tant qu'on ne retire pas.

## Autres points bloquants à traiter avant le feu vert
1. Le robot suit ACWI en **dollars** ; l'ETF du PEA sera en **euros** (et peut-être indexé sur le MSCI World) : prévoir un suivi en euros.
2. Yahoo publie parfois la clôture d'ACWI avec 1 jour de bourse de retard (17, 20 et 23/11) : prévoir une deuxième source pour le cœur.
