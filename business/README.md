# Business qui rapportent : le plan (novembre 2026)

Principe : vendre un **résultat** à des gens qui paient déjà pour ce problème, en faisant
faire la majorité du travail par l'IA et par des outils open source. Coût de départ ≈ 0 €.

## 1. Accompagnement « facture électronique » des TPE (priorité n°1 en France)

- **Le déclencheur :** depuis le 1er septembre 2026, toutes les entreprises assujetties à la TVA doivent pouvoir
  **recevoir** des factures électroniques ; au 1er septembre 2027, les PME, TPE et micro-entreprises devront
  aussi les **émettre** via une plateforme agréée. Des centaines de milliers d'artisans ne sont pas prêts.
  (Dates selon éditeurs et cabinets ; à confirmer sur impots.gouv.fr.)
- **L'offre :** forfait 150–400 € : choix de la plateforme, paramétrage, import des clients, formation d'une heure.
  Plus un abonnement optionnel de 30–50 €/mois pour le suivi.
- **Outils :** le skill `bookkeeping-close` du dépôt, des modèles de documents, un site d'une page.
- **Premiers clients :** artisans et commerçants de ta ville, en porte-à-porte, sur les groupes Facebook locaux
  et via les experts-comptables débordés (proposer de la sous-traitance).

## 2. Agence IA locale (sites, avis Google, réseaux sociaux, standard téléphonique)

- Prix du marché constatés : 500–1 500 €/mois en forfait PME, 500–3 000 € par projet.
- **L'offre de départ :** site vitrine + fiche Google optimisée + réponses aux avis : 490 € puis 49 €/mois.
- **Outils :** Cloudflare Pages ou Workers (déjà configuré, gratuit), les skills `ig-*`, `nextjs-developer` et `cold-email-sequence-generator`.

## 3. Chaîne YouTube ou TikTok « sans visage »

- Production complète déjà dans le dépôt : `yt-script` → voix ElevenLabs → `openverse-sfx` ou `real-sound` → montage.
- Thème cohérent avec le robot : « Un robot IA gère 10 000 $ en public ». Le journal quotidien du robot sert de
  contenu, et la transparence (y compris les pertes) est l'argument.
- **Revenus :** publicité (lente), affiliation (courtiers, livres), puis produit propre.

## 4. Newsletter ou produit numérique « marchés »

- Rapport hebdomadaire automatique : régime de marché, crypto, positions du robot.
- Gratuit au départ (Substack ou Beehiiv), payant à 5–9 €/mois une fois une audience constituée.
- **Attention :** ne jamais promettre de gains ni donner de conseil personnalisé. En France, le conseil en
  investissement est réglementé (statut CIF, AMF) ; rester sur de l'information et de l'éducation.

## 5. Micro-SaaS open source (plus long, plus gros potentiel)

- **Modèle prouvé :** cœur open source gratuit + version hébergée payante (exemples : Cal.com, Plausible).
- **Idée cohérente avec le n°1 :** un outil simple de conformité facture électronique pour micro-entrepreneurs,
  ou un tableau de bord de trésorerie sur 13 semaines (skill `cash-flow-forecaster`).
- Ne coder qu'**après** avoir vendu le service à la main à 10 clients : on sait alors quoi automatiser.

## Ordre conseillé

1. Semaine 1 : offre n°1 ou n°2 écrite, site d'une page, 50 prospects contactés.
2. Mois 1 : 3 premiers clients payants → témoignages.
3. Mois 2–3 : contenu (n°3/n°4) sur le parcours et le robot, en parallèle.
4. Mois 6 : automatiser ce qui se répète → micro-SaaS (n°5).
