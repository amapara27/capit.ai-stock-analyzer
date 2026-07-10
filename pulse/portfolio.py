import json

import pandas as pd
import yfinance as yf

from pulse.config import PORTFOLIO_PATH

RETURN_WINDOWS = {"5d": 5, "1mo": 21, "3mo": 63, "1y": 252}  # trading days


def load_portfolio(path: str = PORTFOLIO_PATH) -> list[dict]:
    with open(path) as f:
        holdings = json.load(f)
    for h in holdings:
        if not all(k in h for k in ("ticker", "shares", "cost_basis")):
            raise ValueError(f"Holding missing ticker/shares/cost_basis: {h}")
    return holdings


def snapshot(holdings: list[dict]) -> dict:
    """Portfolio snapshot: positions, weights, returns vs SPY, risk flags."""
    tickers = [h["ticker"] for h in holdings]
    # 2y so the 252-trading-day (1y) window has enough rows
    prices = yf.download(tickers + ["SPY"], period="2y", auto_adjust=True, progress=False)["Close"]
    prices = prices.dropna(how="all").ffill()

    latest = prices.iloc[-1]
    positions = []
    for h in holdings:
        price = float(latest[h["ticker"]])
        value = price * h["shares"]
        positions.append({
            **h,
            "price": round(price, 2),
            "value": round(value, 2),
            "gain_pct": round((price / h["cost_basis"] - 1) * 100, 1),
        })

    total = sum(p["value"] for p in positions)
    for p in positions:
        p["weight_pct"] = round(p["value"] / total * 100, 1)

    # Value-weighted portfolio returns vs SPY per window
    returns = {}
    shares = pd.Series({h["ticker"]: h["shares"] for h in holdings})
    port_value = (prices[tickers] * shares).sum(axis=1)
    for name, days in RETURN_WINDOWS.items():
        if len(prices) > days:
            returns[name] = {
                "portfolio_pct": round((port_value.iloc[-1] / port_value.iloc[-days - 1] - 1) * 100, 1),
                "spy_pct": round((prices["SPY"].iloc[-1] / prices["SPY"].iloc[-days - 1] - 1) * 100, 1),
            }

    flags = []
    high_52w = prices[tickers].iloc[-252:].max()  # last trading year only
    for p in positions:
        t = p["ticker"]
        if p["weight_pct"] > 25:
            flags.append(f"{t} is {p['weight_pct']}% of portfolio (concentration risk)")
        drawdown = (1 - latest[t] / high_52w[t]) * 100
        if drawdown > 20:
            flags.append(f"{t} is {drawdown:.0f}% below its 52-week high")
        if p["gain_pct"] < -20:
            flags.append(f"{t} is {-p['gain_pct']:.0f}% underwater vs cost basis")

    return {
        "positions": positions,
        "total_value": round(total, 2),
        "returns": returns,
        "flags": flags,
    }


if __name__ == "__main__":
    snap = snapshot(load_portfolio())
    print(json.dumps(snap, indent=2, default=str))
    assert snap["total_value"] > 0 and snap["returns"], "snapshot missing value or returns"
