from dotenv import load_dotenv
load_dotenv()

import os
import pandas as pd
from llama_index.experimental.query_engine import PandasQueryEngine

from prompts import NEW_PROMPT, INSTRUCTION_PROMPT, CONTEXT, TOOL_DESCRIPTIONS

from llama_index.core.tools import QueryEngineTool, ToolMetadata, FunctionTool
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.agent.workflow import AgentWorkflow

import asyncio
import logging

logging.getLogger("httpx").setLevel(logging.WARNING)

class StockAnalyzerAgent:
    def __init__(self, model="gpt-3.5-turbo", verbose=True):
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

    # Gets summary from the news
    def _get_news_summary(self) -> str:
        try:
            # For now, return a simple message. You can enhance this to load from CSV
            # or call StockDataService.get_stock_news()
            return "News tool not yet fully implemented. Run stockdata.py first to generate news data."
        except Exception as e:
            return f"Error loading news: {str(e)}"

    # Builds all the tools for the agent
    def build_tools(self):
        tools = []

        # Tool 1: Price Data Analysis
        try:
            price_engine = self._build_query_engine("data/historical_prices.csv")
            tools.append(QueryEngineTool(
                query_engine=price_engine,
                metadata=ToolMetadata(
                    name="parse_price_data",
                    description=TOOL_DESCRIPTIONS["parse_price_data"],
                ),
            ))
        except FileNotFoundError:
            logging.warning("historical_prices.csv not found. Run stockdata.py first.")

        # Tool 2: Financial Data Analysis
        try:
            financial_engine = self._build_query_engine("data/financials.csv")
            tools.append(QueryEngineTool(
                query_engine=financial_engine,
                metadata=ToolMetadata(
                    name="parse_financial_data",
                    description=TOOL_DESCRIPTIONS["parse_financial_data"],
                ),
            ))
        except FileNotFoundError:
            logging.warning("financials.csv not found. Run stockdata.py first.")

        # Tool 3: Metrics Analysis
        try:
            metrics_engine = self._build_query_engine("data/metrics.csv")
            tools.append(QueryEngineTool(
                query_engine=metrics_engine,
                metadata=ToolMetadata(
                    name="parse_metrics",
                    description=TOOL_DESCRIPTIONS["parse_metrics"],
                ),
            ))
        except FileNotFoundError:
            logging.warning("metrics.csv not found. Run stockdata.py first.")

        # Tool 4: News Analysis (function tool for now)
        news_tool = FunctionTool.from_defaults(
            fn=self._get_news_summary,
            name="parse_news",
            description=TOOL_DESCRIPTIONS["parse_news"]
        )
        tools.append(news_tool)

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
