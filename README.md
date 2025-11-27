# Capit.ai 🤖📈

An AI-powered stock analysis assistant that combines quantitative data, financial statements, valuation metrics, and news sentiment to provide comprehensive investment insights.

---

## About The Project

Capit.ai is a multi-tool RAG (Retrieval-Augmented Generation) agent that analyzes stocks across four dimensions:

1. **Price Analysis** - Historical trends, volatility, and technical patterns
2. **Financial Health** - Revenue growth, margins, cash flow from financial statements
3. **Valuation Metrics** - P/E ratios, debt levels, profitability indicators
4. **News Sentiment** - Recent headlines and market catalysts

The agent synthesizes data from these sources to provide insights like:
- "AAPL's P/E of 28 is elevated, but justified by 15% revenue growth and strong free cash flow"
- "Recent AI product launch news explains the 10% price spike last week"

### Key Features
* **Multi-source analysis:** Combines price data, financials, metrics, and news
* **Semantic search:** Vector store indexes for intelligent news analysis
* **Insightful synthesis:** Goes beyond data retrieval to provide "so what?" analysis
* **Extensible:** Built with classes for easy integration into web apps or APIs

---

## Getting Started

### Prerequisites
* Python 3.8+
* OpenAI API key (for GPT-3.5-turbo or GPT-4)
* Internet connection (for fetching yfinance data)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/capit.ai.git
    cd capit.ai
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

    Required packages:
    - `yfinance` - Stock data API
    - `llama-index` - RAG framework
    - `pandas`, `numpy` - Data processing
    - `plotly` - Interactive charts
    - `python-dotenv` - Environment variables
    - `openai` - LLM API

3.  **Set up environment variables:**
    Create a `.env` file in the project root:
    ```bash
    OPENAI_API_KEY=your_openai_api_key_here
    STOCK_TICKER=AAPL  # Optional: default ticker for news analysis
    ```

---

## Usage

### Step 1: Generate Stock Data

Run `stockdata.py` to fetch and process stock data:

```bash
python stockdata.py
```

**What it does:**
- Prompts you for years to look back (e.g., `2`)
- Prompts you for a ticker symbol (e.g., `NVDA`)
- Fetches historical prices, financials, metrics, and news
- Saves to CSV files in `data/` directory:
  - `historical_prices.csv` - OHLCV data
  - `financials.csv` - Income statement, balance sheet, cash flow
  - `metrics.csv` - P/E, ROE, margins, debt ratios, etc.
  - `news.csv` - Recent headlines and metadata

### Step 2: Run the Analysis Agent

Start the interactive CLI agent:

```bash
python rag.py
```

**Example queries:**
- "What's NVDA's P/E ratio and is it justified by growth?"
- "Analyze the revenue trend over the last 4 quarters"
- "What recent news could explain the price movement?"
- "Is the stock overvalued based on fundamentals?"
- "Calculate volatility and compare to recent highs"

**How it works:**
- The agent uses 4 tools to analyze your query:
  - `parse_price_data` - Queries historical price CSV
  - `parse_financial_data` - Queries financials CSV
  - `parse_metrics` - Queries metrics CSV
  - `parse_news` - Semantic search over news vector index
- It synthesizes insights across all data sources
- Provides context and "so what?" analysis, not just raw numbers

Type `q` to quit.

---

## Project Structure

```
capit.ai/
├── stockdata.py          # Data fetching service (StockDataService class)
├── rag.py                # Analysis agent (StockAnalyzerAgent class)
├── prompts.py            # Agent prompts and tool descriptions
├── data/                 # Generated CSV files (gitignored)
│   ├── historical_prices.csv
│   ├── financials.csv
│   ├── metrics.csv
│   └── news.csv
├── .env                  # API keys (gitignored)
└── README.md
```

---

## Example Workflow

```bash
# 1. Fetch data for NVDA over 2 years
$ python stockdata.py
Enter number of years to look back: 2
Enter stock ticker: NVDA

# 2. Set ticker for news analysis (optional)
$ export STOCK_TICKER=NVDA

# 3. Start the agent
$ python rag.py
Enter a prompt (or q to quit): Analyze NVDA's valuation and recent performance

# Agent response:
# "NVDA's P/E ratio of 45 is elevated compared to the tech sector average of 30.
# However, this premium is justified by exceptional revenue growth of 265% YoY,
# driven by AI chip demand. Recent news shows the company announced new data center
# partnerships, which explains the 12% price increase over the past week.
# The stock trades at a PEG ratio of 1.2, suggesting reasonable valuation given growth.
# Note: This is not financial advice."
```

---

## 🗺️ Roadmap

### Phase 1: Backend Foundation ✅
- [x] Refactor into reusable classes (`StockDataService`, `StockAnalyzerAgent`)
- [x] Add 4 analysis tools (price, financials, metrics, news)
- [x] Implement vector store for news analysis
- [x] Create comprehensive prompts for insightful synthesis

### Phase 2: Real-time News & Sentiment (In Progress)
- [x] Integrate yfinance news API
- [x] Vector store indexing for semantic search
- [ ] Sentiment analysis with LLM scoring
- [ ] External news APIs (Alpha Vantage, Finnhub)

### Phase 3: Quantitative Models
- [ ] Technical indicators (RSI, MACD, Bollinger Bands)
- [ ] Volatility metrics (Beta, VaR, Sharpe ratio)
- [ ] Correlation analysis vs benchmarks

### Phase 4: Web Dashboard
- [ ] FastAPI backend with REST endpoints
- [ ] React/Next.js frontend
- [ ] Interactive Plotly charts
- [ ] Real-time chat interface

### Phase 5: Advanced Features
- [ ] Portfolio analysis and risk assessment
- [ ] Monte Carlo simulations
- [ ] Backtesting framework

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
