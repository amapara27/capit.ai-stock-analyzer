# Capit.ai

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
* **Multi-model support:** Works with both OpenAI (GPT) and Anthropic (Claude) models
* **Interactive CLI:** Real-time question-answering interface
* **Price visualization:** Interactive Plotly charts for stock price history

---

## Getting Started

### Prerequisites
* Python 3.8+
* OpenAI API key and/or Anthropic API key
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
    - `llama-index-llms-anthropic` - Anthropic/Claude integration
    - `pandas`, `numpy` - Data processing
    - `plotly` - Interactive charts
    - `python-dotenv` - Environment variables
    - `openai` - OpenAI API
    - `anthropic` - Anthropic API

3.  **Set up environment variables:**
    Create a `.env` file in the project root:
    ```bash
    OPENAI_API_KEY=your_openai_api_key_here
    ANTHROPIC_API_KEY=your_anthropic_api_key_here
    ```

---

## Usage

### Option 1: Run via main.py (Recommended)

The main entry point combines data fetching and analysis in one workflow:

```bash
python main.py
```

**What it does:**
- Prompts you for years to look back (e.g., `2`)
- Prompts you for a ticker symbol (e.g., `NVDA`)
- Fetches historical prices, financials, metrics, and news
- Displays an interactive price chart
- Starts the analysis agent for Q&A

### Option 2: Run Separately

#### Step 1: Generate Stock Data

Run `stockdata.py` to fetch and process stock data:

```bash
python stockdata.py
```

**What it does:**
- Prompts you for years to look back (e.g., `2`)
- Prompts you for a ticker symbol (e.g., `NVDA`)
- Fetches historical prices, financials, metrics, and news
- Displays an interactive price chart
- Saves to CSV files in `data/` directory:
  - `historical_prices.csv` - OHLCV data for selected ticker
  - `all_prices.csv` - OHLCV data for top 10 tech stocks
  - `financials.csv` - Income statement, balance sheet, cash flow
  - `metrics.csv` - P/E, ROE, margins, debt ratios, etc.
  - `info.csv` - Full company information
  - `news.csv` - Recent headlines and metadata

#### Step 2: Run the Analysis Agent

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

Type `q` to quit.

---

## Analysis Tools

The agent uses 4 specialized tools to analyze your queries:

| Tool | Description | Data Source |
|------|-------------|-------------|
| `parse_price_data` | Analyzes price trends, volatility, moving averages, volume patterns | `historical_prices.csv` |
| `parse_financial_data` | Examines income statements, balance sheets, cash flow statements | `financials.csv` |
| `parse_metrics` | Evaluates P/E, PEG, ROE, margins, debt ratios, and other KPIs | `metrics.csv` |
| `parse_news` | Semantic search over recent news headlines via vector store index | yfinance news API |

The agent synthesizes insights across all data sources and provides context with every analysis, answering the "so what?" rather than just reporting raw numbers.

---

## Project Structure

```
capit.ai/
├── main.py               # Main entry point (data fetch + analysis)
├── stockdata.py          # Data fetching service (StockDataService class)
├── rag.py                # Analysis agent (StockAnalyzerAgent class)
├── prompts.py            # Agent prompts and tool descriptions
├── requirements.txt      # Python dependencies
├── data/                 # Generated CSV files (gitignored)
│   ├── all_prices.csv
│   ├── historical_prices.csv
│   ├── financials.csv
│   ├── metrics.csv
│   ├── info.csv
│   └── news.csv
├── .env                  # API keys (gitignored)
└── README.md
```

---

## Example Workflow

```bash
# 1. Start the application
$ python main.py
Enter number of years to look back: 2
Enter stock ticker: NVDA

# [Interactive price chart opens in browser]
# [Agent initializes with your data]

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

## Supported Models

The agent auto-detects the model provider based on the model name:

| Provider | Example Models |
|----------|----------------|
| Anthropic | `claude-sonnet-4-5-20250929`, `claude-opus-4-5-20251101` |
| OpenAI | `gpt-4`, `gpt-3.5-turbo` |

Configure the model in `main.py` or `rag.py` by changing the `model` variable.

---

## License

Distributed under the MIT License. See `LICENSE` for more information.
