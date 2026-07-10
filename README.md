# Pulse Trading Assistant

An autonomous trading research agent built on **LangGraph** and **Claude**. It researches the market daily, compares your portfolio to the benchmark, screens small/mid-caps for asymmetric growth, and writes a dated research report — plus an interactive analyst chat over all the same data.

---

## Demo

https://x.com/akmapara/status/2010825574101479671?s=20

---

## How it works

Two LangGraph modes:

**1. Report pipeline** (`python main.py report`) — a deterministic `StateGraph`. Data fetching is pure Python (zero LLM tokens); only two nodes call Claude:

```
START → fetch_market → fetch_news → portfolio → screen
screen ──candidates?──> gems ──> summarize → write_report → END
            └── none ────────────────↑
```

Output: `reports/YYYY-MM-DD.md` with Market Summary, Portfolio Review, Hidden Gems, and Sources. Cron-ready — schedule it and get a report every morning.

**2. Analyst chat** (`python main.py chat`) — a ReAct agent with tools over prices, financials, metrics, your portfolio, the gem screener, and semantic news search. Conversation memory persists across turns.

### Data & storage
- **Prices/financials/metrics:** yfinance
- **News:** Massive (ex-Polygon.io) if `MASSIVE_API_KEY` is set, otherwise yfinance — stored in a persistent **Chroma** vector DB (`chroma/`) with URL-hash dedup, so news accumulates and stays searchable across days. Embeddings are local (ONNX MiniLM) — no OpenAI key needed.
- **Portfolio:** edit `portfolio.json` (`ticker`, `shares`, `cost_basis`)
- **Gem screen:** hand-curated small/mid-cap universe in `pulse/config.py` (`CANDIDATES`), filtered by market cap $300M–$10B, revenue growth >15%, PEG <2 or forward P/E <30, gross margin >30%

---

## Getting Started

### Prerequisites
- Python 3.11 (conda recommended)
- Anthropic API key
- Optional: Massive API key (free tier) for richer news

### Installation

```bash
git clone https://github.com/your-username/pulse-trading-agent.git
cd pulse-trading-agent

conda create -n pulse-trading-agent python=3.11 -y
conda activate pulse-trading-agent
pip install -r requirements.txt

cp .env.example .env   # then paste in your ANTHROPIC_API_KEY
```

Edit `portfolio.json` with your actual holdings.

> First news run downloads Chroma's ~80MB local embedding model — a one-time wait, not a hang.

---

## Usage

```bash
python main.py report            # run the daily research pipeline → reports/YYYY-MM-DD.md
python main.py report --verbose  # same, streaming per-node progress
python main.py chat              # interactive analyst chat (q to quit)
python main.py chart NVDA --years 2   # interactive Plotly price chart
```

**Example chat queries:**
- "How is my portfolio doing vs SPY?"
- "Which of my holdings had news this week?"
- "Run the gem screen and tell me which survivor has the best risk/reward"
- "What's NVDA's P/E and is it justified by growth?"

### Scheduling the daily report (optional)

Any scheduler works — the report command is self-contained:

```bash
# cron: weekdays at 7am
0 7 * * 1-5 cd /path/to/pulse-trading-agent && conda run -n pulse-trading-agent python main.py report
```

---

## Chat Tools

| Tool | Description |
|------|-------------|
| `get_price_history` | Price summary: return, high/low, volatility over a period |
| `get_financials` | Income statement, balance sheet, cash flow |
| `get_stock_metrics` | P/E, PEG, ROE, margins, debt ratios |
| `portfolio_summary` | Positions, weights, returns vs SPY, risk flags |
| `search_stock_news` | Semantic search over the Chroma news store |
| `run_gem_screen` | Screen the candidate universe for hidden gems |

---

## Project Structure

```
pulse-trading-agent/
├── main.py               # CLI: report | chat | chart
├── portfolio.json        # your holdings
├── pulse/
│   ├── config.py         # model, watchlist, gem-screen universe, paths
│   ├── stockdata.py      # yfinance fetchers (StockDataService)
│   ├── portfolio.py      # snapshot: returns vs SPY, weights, risk flags
│   ├── news.py           # Massive/yfinance news + Chroma store & search
│   ├── screener.py       # hidden-gems screen
│   ├── graph.py          # LangGraph: report pipeline + chat agent
│   ├── tools.py          # chat agent @tool functions
│   └── prompts.py        # system + report prompts
├── LEARNING.md           # LangGraph concepts mapped to this codebase
├── reports/              # generated daily reports (gitignored)
├── chroma/               # persistent news vector DB (gitignored)
├── data/                 # CSV cache (gitignored)
└── .env                  # API keys (gitignored)
```

---

## Configuration

- **Model:** defaults to `claude-sonnet-5`; override with `PULSE_MODEL` in `.env`
- **Watchlist / candidates:** edit `WATCHLIST` and `CANDIDATES` in `pulse/config.py`

---

## License

Distributed under the MIT License. See `LICENSE` for more information.

*Pulse analyzes historical data only. Nothing it produces is financial advice.*
