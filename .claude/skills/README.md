# Skills Claude Code

Skills importés depuis [Jeffallan/claude-skills](https://github.com/Jeffallan/claude-skills)
(commit `143243c`, licence MIT — voir `LICENSE-claude-skills`).

Claude Code les charge automatiquement depuis ce dossier `.claude/skills/`.

Skills importés depuis [OneWave-AI/claude-skills](https://github.com/OneWave-AI/claude-skills)
(commit `b2267d9`, dossiers complets avec scripts, licence MIT — voir `LICENSE-onewave`) :
cold-email-sequence-generator, client-proposal-generator, design-export-repair,
ai-readiness-assessment, bi-measure-builder, board-deck-generator, bookkeeping-close,
brand-voice-analyzer, cash-flow-forecaster, competitor-intel-agent.

Skill `taste-skill` (nom : `design-taste-frontend`) importé depuis
[leonxlnx/taste-skill](https://github.com/leonxlnx/taste-skill) (commit `12af471`, licence MIT).

## Prérequis

- Node 22+ (scripts de `taste-skill`, uniquement modules Node intégrés).
- Python 3 + `pip install -r .claude/skills/requirements.txt`.
- LibreOffice (`soffice`) pour `design-export-repair`.

Skill `img2threejs` importé depuis [img2threejs/img2threejs](https://github.com/img2threejs/img2threejs)
(commit `3e7099e`, licence Apache-2.0, sans `.git`/`.github`). Scripts Python stdlib uniquement.

Skill `find-skills` importé depuis [vercel-labs/skills](https://github.com/vercel-labs/skills)
(commit `92a9a34`, licence MIT — voir `find-skills/LICENSE`). Utilise `npx skills` (Node).

Skill `prompt-master` importé depuis [nidhinjs/prompt-master](https://github.com/nidhinjs/prompt-master)
(commit `49b3a72`, licence MIT — voir `prompt-master/LICENSE`). Texte uniquement, aucun script.

Skills Instagram `ig-*` (13 skills : ig-reel, ig-caption, ig-carousel, ig-story, ig-viral, ig-human…)
importés depuis [Jakeschincariol/instagram-agent-skill](https://github.com/Jakeschincariol/instagram-agent-skill)
(commit `d03c56b`, licence MIT — voir `LICENSE-instagram-agent`). Scripts Python stdlib, locaux.
Modèle de profil de voix : `instagram-voice-template.md` (à copier dans `~/.claude/instagram/voice.md`).

Skill `canvas-design` importé depuis [anthropics/skills](https://github.com/anthropics/skills)
(commit `ca45fc4`, licence Apache-2.0 — voir `canvas-design/LICENSE.txt`, polices sous licence OFL).
Skill `banner-design` importé depuis [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)
(commit `28b3b8d`, licence MIT — voir `banner-design/LICENSE`). Sans clé API ni service payant.

Skills de trading (74) importés depuis [tradermonty/claude-trading-skills](https://github.com/tradermonty/claude-trading-skills)
(commit `c9b8419`, licence MIT — voir `LICENSE-trading-tradermonty`). Dépendances : `requirements-trading.txt`.
18 d'entre eux demandent une clé FMP (`FMP_API_KEY`) ; certains Finviz Elite ou Alpaca. Aucune clé n'est fournie.
Skills `trader-*` (11) importés depuis [Jakeschincariol/trader-skill](https://github.com/Jakeschincariol/trader-skill)
(commit `5189e79`, licence MIT — voir `LICENSE-trader-skill`). Python stdlib, données publiques (SEC, Congrès US, Yahoo).
