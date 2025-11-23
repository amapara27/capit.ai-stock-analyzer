import pandas as pd
import datetime as dt
import yfinance as yf
import plotly.graph_objects as go
import os

class StockDataService():
    def __init__(self, output_dir, output_filename):
        self.output_dir = output_dir
        self.output_filename = "stock_data.csv"
        self.full_path = os.path.join(output_dir, output_filename)
        os.makedirs(output_dir, exist_ok=True)
    
    def get_historical_prices(self, years):
        # Sets start and end dates for historical stock data
        end = dt.datetime.now()
        start = end - dt.timedelta(days = years * 365)  # Sets start date based on user input

        # List of stock tickers to get data from
        stockList = ["AAPL", "NVDA", "TSLA", "MSFT", "GOOGL", "AMZN", "META", "NFLX", "INTC", "AMD"]

        # Get historical data based on stockList and date range
        df = yf.download(stockList, start, end)

        return df
    
    def get_stock_data(self, df, ticker):
        return df.xs(ticker, axis=1, level=1)
    
    def get_stock_info(self, ticker):
        return
    
    def get_financials(self, ticker):
        return
    
    def get_key_metrics(self, ticker):
        return
    
    def get_stock_news(self, ticker, limit):
        return
    
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

    def save_to_csv(self, df):
        df.to_csv(self.full_path, index=False)

def main():
    stocks = StockDataService("data/", "stock_data.csv")

    years = int(input("Enter number of years to look back: "))
    ticker = input("Enter stock ticker: ")

    df = stocks.get_historical_prices(years)
    df_stock = stocks.get_stock_data(df, ticker)
    stocks.create_price_chart(df_stock, years, ticker)

    stocks.save_to_csv(df_stock)

if __name__ == "__main__":
    main()
