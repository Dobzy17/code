# Procédure en cas d'incident (vérifiée par trading/tests/test_incidents.py)

| Incident | Robot fictif (paper.py) | Module réel (live/propose.py) | Ce que fait l'utilisateur |
|---|---|---|---|
| Kraken ne répond pas | Bascule sur les cours Yahoo, et l'écrit dans le journal (« Yahoo (secours) ») | **Ne propose AUCUN ordre** : pas de source de secours avec de l'argent réel | Rien. On réessaie la nuit suivante. Ne jamais trader à la main sur d'autres cours. |
| Historique Kraken trop court | Secours Yahoo | Bloqué (« historique insuffisant ») | Rien. |
| Données vieilles de plus de 48 h | — | Bloqué pour l'actif concerné | Vérifier l'état de Kraken (status.kraken.com). |
| Cours qui bouge de plus de 40 % en un jour | — | Bloqué (donnée suspecte) | Vérifier le cours sur deux sources avant toute action. |
| Ordre exécuté à moitié | — | La proposition suivante ne demande que **le reste**, sans doublon (holdings.json mis à jour) | Mettre à jour holdings.json avec ce qui a VRAIMENT été exécuté. |
| Coupe-circuit (−35 %) | S'arrête (« halted ») | Bloque tout | Relire LECONS.md avant de décider. La relance est une décision humaine, jamais automatique. |
