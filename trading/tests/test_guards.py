import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "live"))
import pandas as pd

from guards import Limits, cap_orders, check_account, check_data

L = Limits()


def series(n=200, end="2026-11-16", last_jump=0.0):
    idx = pd.date_range(end=end, periods=n, freq="D")
    s = pd.Series(100.0, index=idx)
    s.iloc[-1] = 100 * (1 + last_jump)
    return s


def test_fresh_data_ok():
    assert check_data(series(), datetime(2026, 11, 17, 3), L) == []


def test_stale_data_blocked():
    assert any("anciennes" in r for r in check_data(series(end="2026-11-10"), datetime(2026, 11, 17, 3), L))


def test_suspicious_move_blocked():
    assert any("suspect" in r for r in check_data(series(last_jump=0.6), datetime(2026, 11, 17, 3), L))


def test_short_history_blocked():
    assert any("insuffisant" in r for r in check_data(series(n=50), datetime(2026, 11, 17, 3), L))


def test_kill_switch():
    assert check_account(64, 100, False, L)
    assert check_account(90, 100, False, L) == []
    assert check_account(90, 100, True, L)


def test_caps():
    orders = [{"actif": "BTC-EUR", "montant_eur": 2000}, {"actif": "ETH-EUR", "montant_eur": -800},
              {"actif": "X", "montant_eur": 300}]
    kept, notes = cap_orders(orders, L)
    assert [o["montant_eur"] for o in kept] == [500, -500]   # 3e ordre : plafond du jour (1000 €) atteint
    assert sum(abs(o["montant_eur"]) for o in kept) <= L.max_daily_eur and notes
