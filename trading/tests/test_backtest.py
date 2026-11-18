import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
import pandas as pd

import backtest as bt
import strategies as st


def test_no_lookahead():
    """Un signal qui « connaît » le cours du jour ne doit rien gagner ce jour-là."""
    idx = pd.date_range("2024-01-01", periods=4, freq="D")
    p = pd.DataFrame({"A": [100, 200, 100, 200]}, index=idx, dtype=float)
    w = pd.DataFrame({"A": [0, 1, 0, 0]}, index=idx, dtype=float)  # achète le jour du +100 %
    eq = bt.run(p, w, cost_bps=0)
    assert eq.iloc[1] == 1.0          # pas de gain le jour de la décision
    assert eq.iloc[2] == 0.5          # on subit le jour suivant (−50 %)


def test_costs_applied():
    idx = pd.date_range("2024-01-01", periods=3, freq="D")
    p = pd.DataFrame({"A": [100.0, 100.0, 100.0]}, index=idx)
    w = pd.DataFrame({"A": [1.0, 1.0, 1.0]}, index=idx)
    eq = bt.run(p, w, cost_bps=20)
    assert abs(eq.iloc[-1] - 0.998) < 1e-9


def test_trend_goes_to_cash_below_sma():
    idx = pd.date_range("2024-01-01", periods=5, freq="D")
    p = pd.DataFrame({"A": [5, 4, 3, 2, 1]}, index=idx, dtype=float)
    assert st.trend_sma(p, 2)["A"].iloc[-1] == 0


def test_clean_spikes_removes_fake_jump():
    from data import clean_spikes
    idx = pd.date_range("2024-01-01", periods=4, freq="D")
    p = pd.DataFrame({"A": [1.0, 5.0, 1.0, 1.1]}, index=idx)
    out, fixed = clean_spikes(p)
    assert out["A"].tolist() == [1.0, 1.0, 1.0, 1.1] and fixed == {"A": 1}


def test_cash_rate_paid_on_uninvested_part():
    idx = pd.date_range("2024-01-01", periods=366, freq="D")
    p = pd.DataFrame({"A": 100.0}, index=idx)
    w = pd.DataFrame({"A": 0.5}, index=idx)
    eq = bt.run(p, w, cost_bps=0, cash_rate=pd.Series(0.0365, index=idx))
    r = 0.0365 / 365
    # jour 1 : rien n'est encore détenu, tout le capital est en cash ; ensuite la moitié
    assert abs(eq.iloc[-1] - (1 + r) * (1 + 0.5 * r) ** 365) < 1e-9


def test_paper_band_hysteresis():
    sys.path.insert(0, str(Path(__file__).parents[2]))
    from trading.paper import decide
    assert decide(104, 100, held=False) is True     # au-dessus de +3 % : achat
    assert decide(102, 100, held=False) is False    # dans la zone, pas en position : on reste dehors
    assert decide(98, 100, held=True) is True       # dans la zone, en position : on garde
    assert decide(96, 100, held=True) is False      # sous −3 % : vente
