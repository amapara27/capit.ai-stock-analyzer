import pandas as pd
import datetime as dt
import yfinance as yf
import plotly.graph_objects as go
import os

class StockDataService():
    def __init__(self, output_dir):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def _path(self, filename):
        return os.path.join(self.output_dir, filename)

    # Fetches historical price for several stocks
    def get_historical_prices(self, years, tickers=None):
        # Sets start and end dates for historical stock data
        end = dt.datetime.now()
        start = end - dt.timedelta(days = years * 365)  # Sets start date based on user input

        # Default watchlist if no tickers given
        stockList = tickers or ["AAPL", "NVDA", "TSLA", "MSFT", "GOOGL", "AMZN", "META", "NFLX", "INTC", "AMD"]

        # Get historical data based on stockList and date range
        df = yf.download(stockList, start, end)
        df.to_csv(self._path("all_prices.csv"))  # index=True keeps the Date column

        return df

    # Uses historical prices to get single stock prices
    def get_single_stock_prices(self, df, ticker):
        df = df.xs(ticker, axis=1, level=1)
        df.to_csv(self._path("historical_prices.csv"))  # Keep index=True (default) to preserve Date column

        return df

    # Gets info on the stock
    def get_info(self, ticker_sym):
        ticker = yf.Ticker(ticker_sym)

        info_dict = ticker.info

        info = pd.DataFrame([info_dict])
        info.to_csv(self._path("info.csv"), index=False)

        return info

    # Uses info df to get certain metrics
    def get_metrics(self, info):

        # Fetch metrics from the info df - drop useless columns
        columns_to_drop = [
        # --- Contact & Location (Not useful for math) ---
        'address1', 'city', 'state', 'zip', 'country', 'phone', 'website', 'irWebsite',

        # --- Text Blobs (Save these for a separate "Summary" tool, not Metrics) ---
        'longBusinessSummary', 'companyOfficers', 'executiveTeam',

        # --- Redundant Classifications (Keep 'industry' and 'sector', drop the keys) ---
        'industryKey', 'industryDisp', 'sectorKey', 'sectorDisp', 'typeDisp',

        # --- API/System Metadata (Useless for analysis) ---
        'maxAge', 'priceHint', 'quoteType', 'quoteSourceName', 'triggerable',
        'customPriceAlertConfidence', 'sourceInterval', 'exchangeDataDelayedBy',
        'gmtOffSetMilliseconds', 'exchangeTimezoneName', 'exchangeTimezoneShortName',
        'marketState', 'esgPopulated', 'tradeable', 'cryptoTradeable',
        'hasPrePostMarketData', 'firstTradeDateMilliseconds', 'messageBoardId',
        'language', 'region', 'fullExchangeName', 'displayName', 'market',

        # --- Real-Time Noise (Bid/Ask are too volatile for general analysis) ---
        'bid', 'ask', 'bidSize', 'askSize',

        # --- Redundant Price Columns (Keep 'currentPrice' or 'regularMarketPrice') ---
        'regularMarketPreviousClose', 'regularMarketOpen', 'regularMarketDayLow',
        'regularMarketDayHigh', 'regularMarketVolume', 'preMarketPrice', 'postMarketPrice',
        'postMarketChange', 'postMarketChangePercent', 'postMarketTime', 'regularMarketTime'
    ]

        metrics = info.drop(columns=columns_to_drop, errors='ignore')
        metrics.to_csv(self._path("metrics.csv"), index=False)

        return metrics

    # Gets financial documents (Balance Sheet, Income Statement, Cashflow)
    def get_financials(self, ticker_sym):
        ticker = yf.Ticker(ticker_sym)

        income_stmt = ticker.income_stmt
        cashflow = ticker.cashflow
        balance_sheet = ticker.balance_sheet

        income_stmt.index = [f"IS_{idx}" for idx in income_stmt.index]
        balance_sheet.index = [f"BS_{idx}" for idx in balance_sheet.index]
        cashflow.index = [f"CF_{idx}" for idx in cashflow.index]

        financials = pd.concat([income_stmt, cashflow, balance_sheet])
        financials = financials.T
        financials.index.name = "Date"

        # Optimizes data format for better RAG readability
        if financials is not None and not financials.empty:
            financials = financials.reset_index()
            # Handle case where index might not be named 'Date'
            if 'Date' not in financials.columns:
                 financials = financials.rename(columns={'index': 'Date'})

            # 2. Add the 'Ticker' column
            financials['Ticker'] = ticker_sym

            # 3. Melt: We removed 'Statement_Type' from id_vars because it doesn't exist yet
            financials = financials.melt(id_vars=['Date', 'Ticker'],
                                         var_name='Financial',
                                         value_name='Value')

            # 4. Create 'Statement_Type' by splitting the prefix (IS_, BS_, CF_)
            # This extracts "IS" from "IS_TotalRevenue"
            financials['Statement_Type'] = financials['Financial'].apply(lambda x: x.split('_')[0])

        financials.to_csv(self._path("financials.csv"), index=False)
        return financials

    # Creates a viewable price chart
    def create_price_chart(self, df, ticker, years):
            close = df["Close"]  # could be single ticker or multiple tickers

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=close.index,
                y=close.values,
                mode='lines',
                name=close.name
            ))

            fig.update_layout(
                title= str(ticker) + " Stock Price Over Last " + str(years) + " Years",
                xaxis_title="Date",
                yaxis_title="Price ($)",
                width=1000,
                height=600,
                xaxis_showgrid=True,
                yaxis_showgrid=True
            )

            fig.show()
