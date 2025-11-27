from dotenv import load_dotenv
load_dotenv()

import os
import pandas as pd

from prompts import NEW_PROMPT, INSTRUCTION_PROMPT, CONTEXT, TOOL_DESCRIPTIONS

from llama_index.experimental.query_engine import PandasQueryEngine
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.core import VectorStoreIndex

import asyncio
import logging

from stockdata import StockDataService

logging.getLogger("httpx").setLevel(logging.WARNING)

class StockAnalyzerAgent:
    def __init__(self, model="gpt-3.5-turbo", verbose=False):
        self.model = model
        self.verbose = verbose
        self.agent = None
        self.workflow = None

    # Builds a PandasQueryEngine for parsing csv files
    def _build_query_engine(self, csv_path: str) -> PandasQueryEngine:
        df = pd.read_csv(csv_path)
        engine = PandasQueryEngine(
            df=df,
            verbose=self.verbose,
            instruction_str=INSTRUCTION_PROMPT
        )
        engine.update_prompts({"pandas_prompt": NEW_PROMPT})
        return engine

    # Builds a VectorStoreIndex from news documents
    def _build_news_index(self, ticker: str):
        try:
            # Load news documents from StockDataService
            service = StockDataService("data/")

            # Gets news focs to fill vector store
            documents = service.get_news(ticker)

            if not documents:
                logging.warning(f"No news found for {ticker}")
                return None

            # Create vector store index from documents
            index = VectorStoreIndex.from_documents(documents)
            return index.as_query_engine()

        except Exception as e:
            logging.error(f"Error building news index: {str(e)}")
            return None

    # Builds all the tools for the agent
    def build_tools(self):
        tools = []

        # Tool 1: Price Data Analysis
        try:
            price_engine = self._build_query_engine("data/historical_prices.csv")

            parse_price_data = QueryEngineTool(
                query_engine=price_engine,
                metadata=ToolMetadata(
                    name="parse_price_data",
                    description=TOOL_DESCRIPTIONS["parse_price_data"],
                ),
            )
            
            tools.append(parse_price_data)

        except FileNotFoundError:
            logging.warning("historical_prices.csv not found. Run stockdata.py first.")

        # Tool 2: Financial Data Analysis
        try:
            financial_engine = self._build_query_engine("data/financials.csv")

            parse_financial_data = QueryEngineTool(
                query_engine=financial_engine,
                metadata=ToolMetadata(
                    name="parse_financial_data",
                    description=TOOL_DESCRIPTIONS["parse_financial_data"],
                ),
            )

            tools.append(parse_financial_data)

        except FileNotFoundError:
            logging.warning("financials.csv not found. Run stockdata.py first.")

        # Tool 3: Metrics Analysis
        try:
            metrics_engine = self._build_query_engine("data/metrics.csv")

            parse_metrics = QueryEngineTool(
                query_engine=metrics_engine,
                metadata=ToolMetadata(
                    name="parse_metrics",
                    description=TOOL_DESCRIPTIONS["parse_metrics"],
                ),
            )

            tools.append(parse_metrics)

        except FileNotFoundError:
            logging.warning("metrics.csv not found. Run stockdata.py first.")

        # Tool 4: News Analysis (vector store index)
        try:
            # Auto-detect ticker from the metrics.csv file
            ticker = None
            try:
                metrics_df = pd.read_csv("data/metrics.csv")
                if 'symbol' in metrics_df.columns:
                    ticker = metrics_df['symbol'].iloc[0]
            except:
                pass

            # Fallback to environment variable or prompt user
            if not ticker:
                ticker = os.getenv("STOCK_TICKER")

            if not ticker:
                ticker = input("Enter the stock ticker for news analysis (must match the ticker used in stockdata.py): ").upper()

            print(f"Loading news for ticker: {ticker}")
            news_engine = self._build_news_index(ticker)

            if news_engine:
                parse_news = QueryEngineTool(
                    query_engine=news_engine,
                    metadata=ToolMetadata(
                        name="parse_news",
                        description=TOOL_DESCRIPTIONS["parse_news"],
                    ),
                )

                tools.append(parse_news)

            else:
                logging.warning("News index could not be built. Skipping news tool.")

        except Exception as e:
            logging.warning(f"Error building news tool: {str(e)}")

        if not tools:
            raise RuntimeError(
                "No data files found! Run 'python stockdata.py' first to generate data."
            )

        return tools

    def initialize(self):
        tools = self.build_tools()
        llm = OpenAI(model=self.model)
        self.agent = ReActAgent(tools=tools, llm=llm, verbose=self.verbose, context=CONTEXT)
        self.workflow = AgentWorkflow([self.agent])
        return self

    async def analyze(self, query):
        if self.workflow is None:
            self.initialize()
        result = await self.workflow.run(query, max_iterations=30)
        return result

async def main():
    agent = StockAnalyzerAgent()
    agent.initialize()

    while True:
        prompt = input("Enter a prompt (or q to quit): ")
        if prompt.lower() == 'q':
            break
        result = await agent.analyze(prompt)
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
