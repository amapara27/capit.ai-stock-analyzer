import datetime as dt
import json
import os
import time

from pulse.config import CANDIDATES, DATA_DIR


def passes(m: dict) -> bool:
    """Hidden-gem heuristic: small/mid cap, growing fast, sanely valued, real margins."""
    mcap = m.get("marketCap") or 0
    growth = m.get("revenueGrowth") or 0
    peg = m.get("trailingPegRatio") or m.get("pegRatio")
    fwd_pe = m.get("forwardPE")
    margin = m.get("grossMargins") or 0
    return (
        300e6 <= mcap <= 10e9
        and growth > 0.15
        and ((peg is not None and 0 < peg < 2) or (fwd_pe is not None and 0 < fwd_pe < 30))
        and margin > 0.30
    )


def screen(candidates: list[str] = CANDIDATES) -> list[dict]:
    """Fetch metrics for each candidate (cached per day) and return screen survivors."""
    cache_path = os.path.join(DATA_DIR, f"screen_cache_{dt.date.today()}.json")
    if os.path.exists(cache_path):
        with open(cache_path) as f:
            all_metrics = json.load(f)
    else:
        import yfinance as yf
        all_metrics = {}
        for t in candidates:
            try:
                all_metrics[t] = yf.Ticker(t).info
            except Exception as e:  # yfinance flakiness: skip and move on
                print(f"  {t}: fetch failed ({e})")
            time.sleep(1)
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(cache_path, "w") as f:
            json.dump(all_metrics, f, default=str)

    keep = ["symbol", "shortName", "sector", "marketCap", "revenueGrowth", "earningsGrowth",
            "trailingPegRatio", "forwardPE", "trailingPE", "grossMargins", "profitMargins",
            "returnOnEquity", "debtToEquity", "currentPrice", "fiftyTwoWeekHigh"]
    return [{k: m.get(k) for k in keep} for m in all_metrics.values() if passes(m)]


if __name__ == "__main__":
    survivors = screen()
    print(f"\n{len(survivors)} survivors of {len(CANDIDATES)} candidates:")
    for s in survivors:
        print(f"  {s['symbol']:6} mcap=${(s['marketCap'] or 0)/1e9:.1f}B "
              f"revGrowth={(s['revenueGrowth'] or 0)*100:.0f}% "
              f"fwdPE={s['forwardPE'] and round(s['forwardPE'], 1)} "
              f"grossMargin={(s['grossMargins'] or 0)*100:.0f}%")
