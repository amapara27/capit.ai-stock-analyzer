import json

import yfinance as yf
from langchain_core.tools import tool

from pulse.config import DATA_DIR
from pulse.news import search_news
from pulse.portfolio import load_portfolio, snapshot
from pulse.screener import screen
from pulse.stockdata import StockDataService

_service = StockDataService(DATA_DIR)


@tool
def get_price_history(ticker: str, period: str = "1y") -> str:
    """Historical price summary for a ticker: recent closes, period return, high/low, volatility.
    period is a yfinance period string like 1mo, 6mo, 1y, 5y."""
    df = yf.download(ticker, period=period, auto_adjust=True, progress=False)["Close"][ticker].dropna()
    if df.empty:
        return f"No price data for {ticker}"
    ret = (df.iloc[-1] / df.iloc[0] - 1) * 100
    vol = df.pct_change().std() * (252 ** 0.5) * 100
    return (f"{ticker} over {period}: last={df.iloc[-1]:.2f}, return={ret:.1f}%, "
            f"high={df.max():.2f}, low={df.min():.2f}, annualized_vol={vol:.1f}%\n"
            f"Last 10 closes:\n{df.tail(10).to_string()}")


@tool
def get_stock_metrics(ticker: str) -> str:
    """Valuation ratios and KPIs for a ticker: P/E, PEG, margins, ROE, debt, market cap."""
    metrics = _service.get_metrics(_service.get_info(ticker))
    return json.dumps(metrics.iloc[0].dropna().to_dict(), indent=1, default=str)


@tool
def get_financials(ticker: str) -> str:
    """Annual financial statements (income, cash flow, balance sheet) in long format."""
    df = _service.get_financials(ticker)
    return df.dropna(subset=["Value"]).to_string(index=False)


@tool
def portfolio_summary() -> str:
    """The user's portfolio: positions, weights, gains, returns vs SPY, and risk flags."""
    return json.dumps(snapshot(load_portfolio()), indent=1, default=str)


@tool
def search_stock_news(query: str, ticker: str = "") -> str:
    """Semantic search over stored news articles. Optional ticker filter (e.g. 'AAPL')."""
    hits = search_news(query, ticker=ticker or None)
    if not hits:
        return "No stored news matches. Run 'python main.py report' to fetch news first."
    return "\n".join(f"- {h['title']} ({h['source']}, {h['date']}) {h['url']}" for h in hits)


@tool
def run_gem_screen() -> str:
    """Run the hidden-gems screen over the candidate universe; returns survivors with metrics.
    Slow on first run each day (~1 min), cached after."""
    survivors = screen()
    return json.dumps(survivors, indent=1, default=str) if survivors else "No survivors today."


ALL_TOOLS = [get_price_history, get_stock_metrics, get_financials,
             portfolio_summary, search_stock_news, run_gem_screen]
