"""Module argent réel — MODE PROPOSITION UNIQUEMENT.

Calcule ce que le robot ferait sur un vrai compte Kraken (cours Kraken en EUR, bougies terminées),
applique tous les garde-fous, et écrit une proposition à valider par un humain.
Il n'existe AUCUN code d'envoi d'ordre dans ce dépôt : c'est voulu.

Positions réelles : à saisir à la main dans live/holdings.json (ou plus tard lues via une clé API
en lecture seule). Usage : python3 trading/live/propose.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from guards import Limits, cap_orders, check_account, check_data
from kraken_data import daily_closes

HERE = Path(__file__).parent
HOLDINGS = HERE / "holdings.json"
SLEEVE = {"BTC-EUR": 0.5, "ETH-EUR": 0.5}   # mêmes règles que paper.py : moitié BTC, moitié ETH
SMA_DAYS, BAND = 150, 0.02                 # trading au-delà de 2 points d'écart à la cible
TREND_BAND = 0.03                          # zone tampon ±3 % autour de la moyenne (accord du 18/11/2026)


def main() -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    lim = Limits()
    h = json.loads(HOLDINGS.read_text()) if HOLDINGS.exists() else \
        {"eur": 0.0, "BTC-EUR": 0.0, "ETH-EUR": 0.0, "peak": 0.0, "halted": False}
    closes = {t: daily_closes(t) for t in SLEEVE}
    last = {t: s.iloc[-1] for t, s in closes.items()}
    equity = h["eur"] + sum(h[t] * last[t] for t in SLEEVE)

    block = check_account(equity, max(h["peak"], equity), h["halted"], lim)
    lines = [f"# Proposition d'ordres réels — {now:%Y-%m-%d %H:%M} UTC", "",
             f"Valeur du compte crypto : {equity:,.2f} €", ""]
    orders = []
    for t, share in SLEEVE.items():
        s = closes[t]
        reasons = check_data(s, now, lim)
        sma = s.rolling(SMA_DAYS).mean().iloc[-1]
        held = h[t] > 0
        last_px = s.iloc[-1]
        on = last_px > sma * (1 + TREND_BAND) or (held and last_px >= sma * (1 - TREND_BAND))
        lines.append(f"- **{t}** clôture {s.index[-1].date()} : {s.iloc[-1]:,.2f} € "
                     f"{'>' if on else '<'} moyenne {SMA_DAYS} j {sma:,.2f} € → cible {share if on else 0:.0%}")
        if reasons:
            lines.append(f"  - ⛔ bloqué : {'; '.join(reasons)}")
            continue
        target = share * equity if on else 0.0
        diff = target - h[t] * last[t]
        if equity > 0 and (abs(diff) / equity > BAND or (not on and h[t] > 0)):
            # vente vers stablecoin (EURC/USDC), pas en euros : pas d'impôt tant qu'on ne retire pas
            orders.append({"actif": t, "montant_eur": round(diff, 2),
                           "sens": "ACHAT" if diff > 0 else "VENTE vers stablecoin"})
    orders, notes = cap_orders(orders, lim)
    lines += ["", "## Ordres proposés (à valider à la main sur Kraken)", ""]
    if block:
        lines += [f"⛔ AUCUN ORDRE : {'; '.join(block)}"]
    else:
        lines += [f"- {o['sens']} {o['actif']} : {abs(o['montant_eur']):,.2f} €" for o in orders] or ["- Aucun."]
        lines += [f"- ⚠️ {n}" for n in notes]
    text = "\n".join(lines) + "\n"
    (HERE / "derniere_proposition.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
