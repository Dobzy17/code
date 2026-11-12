"""Robot de trading en ARGENT FICTIF. Une exécution = une journée.

Usage :
    python3 trading/paper.py           # lit le marché, rééquilibre, écrit le journal
    python3 trading/paper.py --dry     # montre ce qu'il ferait, sans rien enregistrer

Portefeuille (choisi d'après trading/research.py, pas au hasard) :
  * 70 % « cœur »     : ETF actions monde (ACWI), achat-conservation.
                        La recherche montre qu'aucune règle active ne bat ça en actions.
  * 30 % « satellite » : BTC + ETH, seulement quand chacun est au-dessus de sa moyenne
                        150 jours ; sinon cette part reste en cash. Réglage pris au MILIEU
                        de la plage qui marche (50 à 250 j), pas le meilleur du passé.

Garde-fous :
  * frais + glissement de 0,20 % sur chaque ordre ;
  * on ne trade que si l'écart à la cible dépasse 2 points (évite de payer des frais pour rien) ;
  * coupe-circuit : si le capital passe 35 % sous son plus haut, le robot s'arrête et
    attend une décision humaine (mettre "halted": false dans state/portfolio.json).
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd

from data import load_prices

ROOT = Path(__file__).parent
STATE = ROOT / "state" / "portfolio.json"
JOURNAL = ROOT / "state" / "journal.csv"
LOGS = ROOT / "logs"

CORE = {"ACWI": 0.70}
CRYPTO = ["BTC-USD", "ETH-USD"]
CRYPTO_SLEEVE = 0.30
SMA_DAYS = 150
COST = 0.002
BAND = 0.02
KILL_DRAWDOWN = -0.35
START_CASH = 10_000.0


def load_state() -> dict:
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"cash": START_CASH, "positions": {}, "peak": START_CASH, "halted": False,
            "start": date.today().isoformat()}


def targets(prices: pd.DataFrame) -> tuple[dict, dict]:
    """Poids cibles + explication lisible de chaque décision."""
    w, why = dict(CORE), {t: "cœur : toujours investi" for t in CORE}
    for t in CRYPTO:
        s = prices[t].dropna()
        sma = s.rolling(SMA_DAYS).mean().iloc[-1]
        last = s.iloc[-1]
        on = last > sma
        w[t] = CRYPTO_SLEEVE / len(CRYPTO) if on else 0.0
        why[t] = (f"{last:,.0f} $ {'>' if on else '<'} moyenne {SMA_DAYS} j ({sma:,.0f} $) "
                  f"→ {'tendance haussière, investi' if on else 'tendance baissière, en cash'}")
    return w, why


def main(dry: bool = False) -> None:
    tickers = list(CORE) + CRYPTO
    raw = load_prices(tickers, start="2023-01-01", max_age_hours=2)
    idx = pd.date_range(raw.index.min(), raw.index.max(), freq="D")
    prices = raw.reindex(idx).ffill()
    last = prices.iloc[-1]
    today = date.today().isoformat()

    state = load_state()
    if state.get("last_run") == today and not dry:
        print(f"Déjà exécuté aujourd'hui ({today}) : rien à faire.")
        return
    pos = state["positions"]
    equity = state["cash"] + sum(q * last[t] for t, q in pos.items())
    state["peak"] = max(state["peak"], equity)
    dd = equity / state["peak"] - 1

    w, why = targets(prices)
    trades: list[dict] = []
    if dd <= KILL_DRAWDOWN:
        state["halted"] = True
    if not state["halted"]:
        # ventes d'abord (libèrent du cash), achats ensuite
        plan = []
        for t in tickers:
            cur_val = pos.get(t, 0.0) * last[t]
            diff_val = w[t] * equity - cur_val
            must = (w[t] == 0 and cur_val > 0)
            if must or abs(diff_val) / equity > BAND:
                plan.append((t, diff_val))
        for t, diff_val in sorted(plan, key=lambda x: x[1]):
            if diff_val > 0:
                diff_val = min(diff_val, state["cash"] / (1 + COST))
            if abs(diff_val) < 1:
                continue
            qty = diff_val / last[t]
            fee = abs(diff_val) * COST
            pos[t] = pos.get(t, 0.0) + qty
            if abs(pos[t] * last[t]) < 0.01:
                pos.pop(t)
            state["cash"] -= diff_val + fee
            trades.append({"date": today, "actif": t, "sens": "ACHAT" if qty > 0 else "VENTE",
                           "quantite": round(qty, 8), "prix": round(float(last[t]), 4),
                           "montant": round(diff_val, 2), "frais": round(fee, 2)})

    equity = state["cash"] + sum(q * last[t] for t, q in pos.items())
    lines = [f"# Journal du robot – {today}", "",
             f"Capital fictif : **{equity:,.2f} $** (départ {START_CASH:,.0f} $ le {state['start']}, "
             f"{equity / START_CASH - 1:+.2%}) · recul depuis le plus haut : {dd:.1%}", ""]
    if state["halted"]:
        lines += ["**COUPE-CIRCUIT ACTIF** : aucun ordre. Décision humaine requise.", ""]
    lines += ["## Décisions", ""] + [f"- **{t}** cible {w[t]:.0%} — {why[t]}" for t in tickers]
    lines += ["", "## Ordres", ""]
    lines += [f"- {x['sens']} {x['actif']} : {abs(x['montant']):,.2f} $ à {x['prix']:,.2f} "
              f"(frais {x['frais']:.2f} $)" for x in trades] or ["- Aucun : portefeuille déjà aligné."]
    lines += ["", "## Positions", "", f"- Cash : {state['cash']:,.2f} $"]
    lines += [f"- {t} : {q:.6f} × {last[t]:,.2f} = {q * last[t]:,.2f} $ "
              f"({q * last[t] / equity:.0%})" for t, q in pos.items()]
    text = "\n".join(lines) + "\n"
    print(text)
    if dry:
        return

    state["last_run"] = today
    state["last_equity"] = round(equity, 2)
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False))
    LOGS.mkdir(exist_ok=True)
    (LOGS / f"{today}.md").write_text(text)
    new = not JOURNAL.exists()
    with JOURNAL.open("a", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=["date", "actif", "sens", "quantite", "prix", "montant", "frais"])
        if new:
            wr.writeheader()
        wr.writerows(trades)
    with (ROOT / "state" / "equity.csv").open("a") as f:
        f.write(f"{today},{equity:.2f}\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    main(ap.parse_args().dry)
