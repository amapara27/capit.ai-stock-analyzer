import asyncio

from rag import StockAnalyzerAgent
from stockdata import StockDataService

async def main():
    service = StockDataService("data/")

    years = int(input("Enter number of years to look back: "))
    ticker = input("Enter stock ticker: ")

    all_stocks = service.get_historical_prices(years)

    single_stock_prices = service.get_single_stock_prices(all_stocks, ticker)
    service.create_price_chart(single_stock_prices, ticker, years)

    documents = service.get_news(ticker)
    df_financials = service.get_financials(ticker)
    df_info = service.get_info(ticker)
    df_metrics = service.get_metrics(df_info)

    model = "claude-sonnet-4-5-20250929"
    agent = StockAnalyzerAgent(model)
    agent.initialize()

    while True:
        prompt = input("Enter a prompt (or q to quit): ")
        if prompt.lower() == 'q':
            break
        result = await agent.analyze(prompt)
        print(result)


if __name__ == "__main__":
    asyncio.run(main())

