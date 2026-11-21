"""Veille hors marché : derniers chiffres de sources gratuites, avec date et source.
Aucune décision du robot n'en dépend tant qu'un test (LECONS.md) ne l'a pas justifié.
Usage : python3 trading/veille.py  → logs/veille-AAAA-MM-JJ.md
"""
from __future__ import annotations

import csv
import io
from datetime import date
from pathlib import Path

import requests

ROOT = Path(__file__).parent
T = 30
COT = {"Or (COMEX)": "088691", "Pétrole WTI (NYMEX)": "067651", "S&P 500 E-mini (CME)": "13874A",
       "Bitcoin (CME)": "133741"}


def fred(series: str) -> tuple[str, float]:
    r = requests.get("https://fred.stlouisfed.org/graph/fredgraph.csv", params={"id": series}, timeout=T)
    r.raise_for_status()
    rows = [x for x in csv.reader(io.StringIO(r.text))][1:]
    rows = [x for x in rows if x[1] not in (".", "")]
    return rows[-1][0], float(rows[-1][1])


def cot(code: str) -> str:
    r = requests.get("https://publicreporting.cftc.gov/resource/6dca-aqww.json", timeout=T, params={
        "$where": f"cftc_contract_market_code='{code}'", "$order": "report_date_as_yyyy_mm_dd DESC", "$limit": 156})
    r.raise_for_status()
    d = r.json()
    nets = [(int(x["noncomm_positions_long_all"]) - int(x["noncomm_positions_short_all"])) / int(x["open_interest_all"])
            for x in d]
    now, lo, hi = nets[0], min(nets), max(nets)
    idx = (now - lo) / (hi - lo) * 100 if hi > lo else 50
    flag = " ⚠️ positions extrêmes à l'achat" if idx > 90 else " ⚠️ positions extrêmes à la vente" if idx < 10 else ""
    return (f"position nette des spéculateurs {now:+.1%} des contrats ouverts, indice COT 3 ans **{idx:.0f}/100**{flag} "
            f"(rapport du {d[0]['report_date_as_yyyy_mm_dd'][:10]})")


def safe(label: str, fn) -> str:
    try:
        return f"- **{label}** : {fn()}"
    except Exception as e:
        return f"- **{label}** : indisponible ({type(e).__name__})"


def main():
    L = [f"# Veille hors marché — {date.today()}", "",
         "_Chiffres bruts avec leur date. Ce ne sont PAS des signaux de trading : aucun n'a encore passé de test._", "",
         "## Économie américaine (FRED, banque fédérale de Saint-Louis)"]

    def curve():
        d, v = fred("T10Y2Y")
        return f"{v:+.2f} point au {d} — {'inversée (signal historique de récession)' if v < 0 else 'positive (normale)'}"

    def sahm():
        d, v = fred("SAHMREALTIME")
        return f"{v:.2f} au {d} — seuil d'alerte 0,50 : {'⚠️ DÉPASSÉ' if v >= 0.5 else 'non atteint'}"

    def nfci():
        d, v = fred("NFCI")
        return f"{v:+.2f} semaine du {d} — {'conditions plus tendues que la moyenne' if v > 0 else 'conditions plus souples que la moyenne'}"

    def hy():
        d, v = fred("BAMLH0A0HYM2")
        return f"{v:.2f} % au {d} — {'stress élevé' if v > 6 else 'calme' if v < 4 else 'intermédiaire'}"

    L += [safe("Courbe des taux 10 ans − 2 ans (T10Y2Y)", curve),
          safe("Règle de Sahm, chômage (SAHMREALTIME)", sahm),
          safe("Conditions financières (NFCI, 0 = moyenne)", nfci),
          safe("Prime de risque des obligations pourries (BAMLH0A0HYM2)", hy), "", "## Zone euro (BCE)"]

    def ecb():
        r = requests.get("https://data-api.ecb.europa.eu/service/data/FM/D.U2.EUR.4F.KR.DFR.LEV",
                         params={"lastNObservations": 1, "format": "csvdata"}, timeout=T)
        r.raise_for_status()
        x = list(csv.DictReader(io.StringIO(r.text)))[-1]
        return f"{float(x['OBS_VALUE']):.2f} % au {x['TIME_PERIOD']}"

    L += [safe("Taux de dépôt BCE", ecb), "", "## Positions des gros spéculateurs (CFTC, rapport COT hebdomadaire)"]
    L += [safe(name, lambda c=code: cot(c)) for name, code in COT.items()]
    L += ["", "## Crypto : moral et activité réelle"]

    def fng():
        d = requests.get("https://api.alternative.me/fng/", params={"limit": 2}, timeout=T).json()["data"]
        return f"**{d[0]['value']}/100 ({d[0]['value_classification']})**, la veille {d[1]['value']}/100 (alternative.me)"

    def chain(name, unit, scale=1):
        js = requests.get(f"https://api.blockchain.info/charts/{name}", params={"timespan": "60days", "format": "json"},
                          timeout=T).json()["values"]
        last, prev = js[-1]["y"] / scale, js[-31]["y"] / scale
        return f"{last:,.0f} {unit} ({last / prev - 1:+.0%} sur 30 j, blockchain.info)"

    def fees():
        f = requests.get("https://mempool.space/api/v1/fees/recommended", timeout=T).json()
        return f"{f['fastestFee']} sat/vB pour un passage rapide, {f['economyFee']} sat/vB économique — " \
               f"{'réseau calme' if f['fastestFee'] < 10 else 'réseau chargé'} (mempool.space)"

    L += [safe("Indice Peur et Avidité", fng),
          safe("Transactions Bitcoin par jour", lambda: chain("n-transactions", "transactions")),
          safe("Puissance de calcul (hashrate)", lambda: chain("hash-rate", "EH/s", 1e6)),
          safe("Frais du réseau Bitcoin", fees)]
    out = "\n".join(L) + "\n"
    (ROOT / "logs").mkdir(exist_ok=True)
    (ROOT / "logs" / f"veille-{date.today()}.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
