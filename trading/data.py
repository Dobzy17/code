"""Données de marché gratuites via yfinance (open source, données Yahoo Finance).

Les cours sont mis en cache dans trading/cache/ pour éviter de re-télécharger
et pour limiter les erreurs 429 (trop de requêtes) de Yahoo.
"""
from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
import yfinance as yf

CACHE = Path(__file__).parent / "cache"


def load_prices(tickers: list[str], start: str = "2010-01-01", refresh: bool = False,
                max_age_hours: float = 12) -> pd.DataFrame:
    """Cours de clôture ajustés (dividendes et splits inclus), une colonne par actif."""
    CACHE.mkdir(exist_ok=True)
    key = CACHE / f"{'_'.join(sorted(tickers))}_{start}.csv"
    if key.exists() and not refresh and time.time() - key.stat().st_mtime < max_age_hours * 3600:
        return pd.read_csv(key, index_col=0, parse_dates=True)

    last_err: Exception | None = None
    for attempt in range(4):
        try:
            raw = yf.download(tickers, start=start, progress=False, auto_adjust=True, threads=False)
            close = raw["Close"] if isinstance(raw.columns, pd.MultiIndex) else raw[["Close"]]
            if isinstance(close, pd.Series):
                close = close.to_frame(tickers[0])
            close = close.dropna(how="all")
            missing = [t for t in tickers if t not in close.columns or close[t].dropna().empty]
            if missing:
                raise RuntimeError(f"aucune donnée pour {missing}")
            close.index = pd.to_datetime(close.index).tz_localize(None)
            close.to_csv(key)
            return close[tickers]
        except Exception as e:  # réseau ou limite de requêtes : on réessaie
            last_err = e
            time.sleep(2 ** attempt * 3)
    if key.exists():  # mieux vaut des données d'hier que rien, mais on le signale
        print(f"[data] ATTENTION : téléchargement impossible ({last_err}), cache ancien utilisé")
        return pd.read_csv(key, index_col=0, parse_dates=True)[tickers]
    raise RuntimeError(f"Impossible de charger {tickers} : {last_err}")


def clean_spikes(prices: pd.DataFrame, max_jump: float = 3.0) -> tuple[pd.DataFrame, dict]:
    """Neutralise les bonds de plus de +300 % en un jour, presque toujours des erreurs de données
    sur les petites cryptos. Prudent : on garde le cours de la veille (le gain est effacé, jamais créé).
    Renvoie les prix nettoyés et le nombre de jours corrigés par actif."""
    p = prices.copy()
    fixed: dict[str, int] = {}
    for col in p.columns:
        for _ in range(50):
            r = p[col] / p[col].ffill().shift(1) - 1
            bad = r > max_jump
            if not bad.any():
                break
            fixed[col] = fixed.get(col, 0) + int(bad.sum())
            p.loc[bad, col] = float("nan")
            p[col] = p[col].ffill()
    return p, fixed


def yahoo_last_close(ticker: str, now: float | None = None, fetch=None) -> tuple[str, float] | None:
    """Secours pour la DERNIÈRE clôture quand la ligne du jour de Yahoo est vide (leçon 58).
    Utilise le cours de clôture des métadonnées du graphique, seulement si la séance est TERMINÉE
    (séance du jour finie et cours pris à la clôture, ou dernier cours antérieur à l'ouverture du jour) : jamais un cours en cours de séance.
    Renvoie (date AAAA-MM-JJ dans le fuseau de la bourse, prix) ou None."""
    import datetime as _dt

    import requests

    if fetch is None:
        def fetch(t):
            r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{t}", params={"range": "5d", "interval": "1d"},
                             headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
            r.raise_for_status()
            return r.json()
    try:
        meta = fetch(ticker)["chart"]["result"][0]["meta"]
        reg = meta["currentTradingPeriod"]["regular"]
        start, end = reg.get("start", reg["end"]), reg["end"]
        t_last = meta["regularMarketTime"]
        now = time.time() if now is None else now
        today_done = now >= end and t_last >= end - 120          # séance du jour terminée, cours de clôture
        previous_session = t_last < start and now < end          # séance du jour pas finie : le dernier cours est celui d'hier
        if not (today_done or previous_session):
            return None
        tz = _dt.timezone(_dt.timedelta(seconds=meta.get("gmtoffset", 0)))
        return _dt.datetime.fromtimestamp(t_last, tz).strftime("%Y-%m-%d"), float(meta["regularMarketPrice"])
    except Exception:
        return None
