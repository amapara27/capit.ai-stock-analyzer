import pandas as pd
import datetime as dt
import yfinance as yf
import plotly.graph_objects as go
import os


# Setting up path to save the csv file
output_directory = r"data"
output_filename = "stock_data.csv"
full_path = os.path.join(output_directory, output_filename)
os.makedirs(output_directory, exist_ok=True)

# Receives user input for number of years to look back
years = int(input("Enter number of years to look back: "))

# Receives user input for stock ticker
ticker = input("Enter stock ticker: ")

# Gets stock data
def get_stock_data(years):

    # Sets start and end dates for historical stock data
    end = dt.datetime.now()
    start = end - dt.timedelta(days = years * 365)  # Sets start date based on user input

    # List of stock tickers to get data from
    stockList = ["AAPL", "NVDA", "TSLA", "MSFT", "GOOGL", "AMZN", "META", "NFLX", "INTC", "AMD"]

    # Get historical data based on stockList and date range
    df = yf.download(stockList, start, end)

    return df

# Gets data for a single stock
def get_single_stock_data(df, ticker: str):
    return df.xs(ticker, axis=1, level=1)

# Creates a plotly (interactive chart)
def get_plot(df, years, ticker):
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


df = get_stock_data(years)
df_stock = get_single_stock_data(df, ticker)
get_plot(df_stock, years, ticker)

# Write the DataFrame to CSV
df_stock.to_csv(full_path, index=False) 

print(f"DataFrame saved to: {full_path}")







