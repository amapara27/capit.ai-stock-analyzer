import os

# Claude model for all LLM calls; override with PULSE_MODEL env var
MODEL = os.getenv("PULSE_MODEL", "claude-sonnet-5")

DATA_DIR = "data/"
CHROMA_DIR = "chroma/"
REPORTS_DIR = "reports/"
PORTFOLIO_PATH = "portfolio.json"

# Tickers researched daily alongside portfolio holdings
WATCHLIST = ["AAPL", "NVDA", "TSLA", "MSFT", "GOOGL", "AMZN", "META", "NFLX", "INTC", "AMD"]

# ponytail: static hand-curated small/mid-cap universe for the gem screen;
# swap for a screener API when a free one exists
CANDIDATES = [
    # Semis / hardware
    "RMBS", "SITM", "POWI", "CRUS", "AMBA", "ALGM", "SLAB",
    # Software / internet
    "GLBE", "DUOL", "APPF", "BRZE", "GTLB", "PCOR", "DOCN", "FIVN", "ALRM",
    # Fintech
    "PAYO", "MQ", "FLYW",
    # Healthcare / biotech tools
    "TMDX", "INSP", "IRTC", "PGNY", "MEDP",
    # Industrials / energy tech
    "ATKR", "PLPC", "AAON", "ESE",
    # Consumer
    "WING", "CAVA", "DKS", "BOOT", "ONON",
    # Materials / specialty
    "HWKN", "IOSP",
]
