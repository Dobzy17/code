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
