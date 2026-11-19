"""Exercices d'incident : ce que font le robot et le module réel quand ça se passe mal."""
import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "live"))

import paper  # noqa: E402
import propose  # noqa: E402


def rising(n=400, end="2026-11-18", start_px=100.0):
    idx = pd.date_range(end=end, periods=n, freq="D")
    return pd.Series([start_px * 1.002 ** i for i in range(n)], index=idx)


def boom(_t):
    raise ConnectionError("Kraken injoignable")


def test_paper_falls_back_to_yahoo_when_kraken_down(monkeypatch):
    monkeypatch.setattr(paper, "daily_closes", boom)
    s, src = paper.crypto_closes("BTC-USD", rising())
    assert src == "Yahoo (secours)" and len(s) == 400


def test_paper_falls_back_when_kraken_history_too_short(monkeypatch):
    monkeypatch.setattr(paper, "daily_closes", lambda t: rising(n=50))
    assert paper.crypto_closes("BTC-USD", rising())[1] == "Yahoo (secours)"


def test_real_module_refuses_without_kraken(monkeypatch, tmp_path):
    monkeypatch.setattr(propose, "daily_closes", boom)
    monkeypatch.setattr(propose, "HERE", tmp_path)
    text = propose.main(datetime(2026, 11, 19, 3))
    assert "AUCUN ORDRE" in text and "indisponibles" in text


def _setup(monkeypatch, tmp_path, holdings):
    f = tmp_path / "holdings.json"
    f.write_text(json.dumps(holdings))
    monkeypatch.setattr(propose, "HOLDINGS", f)
    monkeypatch.setattr(propose, "HERE", tmp_path)
    monkeypatch.setattr(propose, "daily_closes", lambda t: rising())  # tendance haussière nette


def test_partial_fill_next_proposal_completes(monkeypatch, tmp_path):
    """Ordre d'achat exécuté à moitié : la proposition suivante ne demande que le reste, sans doublon."""
    px = rising().iloc[-1]
    _setup(monkeypatch, tmp_path, {"eur": 300.0, "BTC-EUR": 0.0, "ETH-EUR": 0.0, "peak": 300.0, "halted": False})
    first = propose.main(datetime(2026, 11, 19, 3))
    assert "ACHAT BTC-EUR : 150.00 €" in first
    _setup(monkeypatch, tmp_path, {"eur": 225.0, "BTC-EUR": 75.0 / px, "ETH-EUR": 0.0, "peak": 300.0, "halted": False})
    second = propose.main(datetime(2026, 11, 19, 3))
    assert "ACHAT BTC-EUR : 75.00 €" in second and "ACHAT ETH-EUR : 150.00 €" in second


def test_kill_switch_blocks_everything(monkeypatch, tmp_path):
    _setup(monkeypatch, tmp_path, {"eur": 100.0, "BTC-EUR": 0.0, "ETH-EUR": 0.0, "peak": 300.0, "halted": False})
    assert "AUCUN ORDRE" in propose.main(datetime(2026, 11, 19, 3))


def test_stale_data_blocks_orders(monkeypatch, tmp_path):
    _setup(monkeypatch, tmp_path, {"eur": 300.0, "BTC-EUR": 0.0, "ETH-EUR": 0.0, "peak": 300.0, "halted": False})
    text = propose.main(datetime(2026, 11, 25, 3))   # dernière bougie du 18/11 : 6 jours de retard
    assert "bloqué" in text and "ACHAT" not in text
