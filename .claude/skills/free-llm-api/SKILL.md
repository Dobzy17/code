---
name: free-llm-api
description: Fiche des fournisseurs d'IA (LLM) qui offrent un accès API gratuit, avec leurs limites, conditions et pièges (vérifiée le 1er novembre 2026). À consulter quand l'utilisateur cherche une API d'IA gratuite, veut brancher un modèle sans payer, compare des offres gratuites (Gemini, Groq, OpenRouter, Mistral, Cloudflare, NVIDIA, Cohere…) ou demande « quelle IA gratuite utiliser pour mon projet ».
---

# API d'IA gratuites — fiche de référence

Remplace la liste `cheahjs/free-llm-api-resources`, retirée de GitHub (404 constaté le 1er novembre 2026).

**Vérifiée le 1er novembre 2026, à partir de sites de comparaison et de blogs**, pas des pages
officielles de chaque fournisseur (inaccessibles depuis la session de rédaction). Les offres
gratuites changent souvent : **toujours revérifier sur la page officielle du fournisseur avant de
construire quoi que ce soit dessus**, et le dire à l'utilisateur.

## Règles à appliquer avant de recommander une offre

1. **Jamais de données personnelles réelles** envoyées à une offre gratuite qui entraîne ses modèles
   sur les requêtes (Google AI Studio gratuit hors Europe, Mistral offre d'essai…). Pour CLINQ, cela
   exclut tout envoi de données clients ou bars réels.
2. **Europe** : l'utilisateur est en France. Vérifier les restrictions UE/EEE (voir Google ci-dessous).
3. **Aucune activation payante sans accord explicite** de l'utilisateur, même un « petit » crédit de
   10 $ (voir OpenRouter).
4. **Aucune clé dans le dépôt** : la clé va dans une variable d'environnement ou les secrets de
   l'environnement, jamais dans le code ni dans la conversation.
5. Préciser que les gratuits **refusent les requêtes** quand la limite est atteinte (erreur 429) :
   pas de facturation surprise, mais l'appli doit savoir gérer ce refus.

## Offres gratuites permanentes (sans carte bancaire, d'après les sources)

| Fournisseur | Limites gratuites rapportées | Modèles | Points d'attention |
|---|---|---|---|
| **OpenRouter** | 20 requêtes/min ; **50 requêtes/jour**, 1 000/jour si le compte a acheté au moins 10 $ de crédits (cumul historique) | modèles suffixés `:free` (varie) | Limite par compte, pas par modèle ; les échecs comptent ; un solde négatif bloque les gratuits. Une seule clé donne accès à beaucoup de modèles (compatible API OpenAI). Chiffres concordants entre doc officielle et guides. |
| **Groq** | ~30 requêtes/min, ~1 000 requêtes/jour et ~200 000 tokens/jour **par modèle** | surtout gpt-oss et Qwen (Llama retiré du gratuit selon une source) | Très rapide. Les anciens guides citent 14 400 req/jour : périmé. |
| **Google AI Studio (Gemini)** | 5 à 15 req/min ; **20 à 1 500 req/jour selon le modèle** (Google ne publie plus les chiffres, voir sa console) | Flash et Flash-Lite ; **les modèles Pro sont payants depuis avril 2026** | ⚠️ **Europe (UE/EEE), Royaume-Uni, Suisse** : les conditions de Google interdisent d'utiliser le gratuit pour servir des utilisateurs dans ces pays ; la facturation doit être activée. Hors Europe, les requêtes gratuites peuvent servir à entraîner Google et être lues par des humains. À vérifier sur ai.google.dev avant usage. |
| **Mistral (« Free mode »)** | non publiées ; visibles dans l'admin du compte (l'ancien chiffre « ~1 milliard de tokens/mois » date de l'ancienne offre « Experiment ») | modèles Mistral | Entreprise française. L'ancienne offre exigeait d'accepter l'entraînement sur les données et une vérification par téléphone ; vérifier les conditions actuelles. |
| **Cloudflare Workers AI** | **10 000 « neurons » par jour** (partagés entre modèles), 300 req/min en génération de texte | ~40 modèles ouverts | Certains modèles (Kimi K2.6/K2.7, GLM 5.2) sont passés en payant fin juillet 2026. |
| **NVIDIA NIM (programme développeur)** | ~40 req/min selon des listes, pas de limite officielle publiée | 100+ modèles ouverts | Prévu pour le **prototypage**. Vérification par téléphone signalée. |
| **Cohere (clé d'essai)** | ~100 req/jour **ou** 1 000 appels/mois selon les sources (contradictoire) | Command, Aya, embeddings | **Usage non commercial uniquement** → exclu pour CLINQ en production. |

## Offres qui ne sont plus gratuites (ne pas recommander)

- **GitHub Models** : service retiré le 30 juillet 2026.
- **Cerebras** : plus de gratuit permanent depuis le 16 juillet 2026 (essai de 5 $ sur 30 jours avec carte).
- **SambaNova** : essai de 5 $, carte demandée selon une source.
- **Modèles « phares »** (GPT-5.x, Claude Opus, Gemini Pro) : réservés aux offres payantes.

## Solution 100 % gratuite et privée

**Ollama** (logiciel libre) fait tourner des modèles ouverts **sur votre propre ordinateur** : aucune
limite, aucune donnée envoyée à l'extérieur. Il faut un ordinateur assez puissant (idéalement
16 Go de mémoire ou plus) ; les modèles sont moins forts que les meilleurs modèles en ligne.

## Recommandation par défaut

- **Pour tester rapidement plusieurs modèles** : OpenRouter (une seule clé, modèles `:free`).
- **Pour la vitesse** : Groq.
- **Pour un projet européen avec des données réelles** : aucune offre gratuite n'est sûre côté données ;
  privilégier Ollama en local, ou une offre payante avec engagement de non-entraînement (à valider
  avec l'utilisateur, car c'est une dépense).

## Sources (consultées le 1er novembre 2026)

- OpenRouter — limites des modèles gratuits : https://openrouter.ai/pricing ,
  https://openrouter.zendesk.com/hc/en-us/articles/39501163636379-OpenRouter-Rate-Limits-What-You-Need-to-Know ,
  https://www.truefoundry.com/blog/openrouter-rate-limits-your-free-tier-depends-on-what-youve-already-paid
- Comparatif OpenRouter « 13 options » : https://openrouter.ai/blog/tutorials/free-llm-apis-compared/
- Gemini : https://ai.google.dev/gemini-api/docs/rate-limits , https://www.lilachbullock.com/is-gemini-api-free/ ,
  https://yingtu.ai/en/blog/google-gemini-api-free-tier-limits-2026 , https://klymentiev.com/blog/gemini-api-free-tier
- Groq, Cerebras, Mistral : https://grokified.com/blog/free-llm-api , https://www.eesel.ai/blog/groq-pricing ,
  https://klymentiev.com/blog/free-llm-api
- Cloudflare, NVIDIA, GitHub Models : https://www.developersdigest.tech/models/free-api ,
  https://agentdeals.dev/vendor/github-models
- Listes communautaires : https://github.com/amardeeplakshkar/awesome-free-llm-apis ,
  https://github.com/mnfst/awesome-free-llm-apis , https://github.com/nejib1/Free-LLM
