from dotenv import load_dotenv
load_dotenv()

import os
import pandas as pd
from llama_index.experimental.query_engine import PandasQueryEngine

from prompts import NEW_PROMPT, INSTRUCTION_PROMPT, CONTEXT, TOOL_DESCRIPTIONS

from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.agent.workflow import AgentWorkflow

import asyncio
import logging

logging.getLogger("httpx").setLevel(logging.WARNING)


class StockAnalyzerAgent:
    def __init__(self, model="gpt-3.5-turbo", verbose=True, data_path="data/stock_data.csv"):
        self.model = model
        self.verbose = verbose
        self.data_path = data_path
        self.df = None
        self.query_engine = None
        self.agent = None
        self.workflow = None

    def load_data(self):
        self.df = pd.read_csv(self.data_path)
        return self.df

    def build_query_engine(self):
        if self.df is None:
            self.load_data()
        self.query_engine = PandasQueryEngine(
            df=self.df, verbose=self.verbose, instruction_str=INSTRUCTION_PROMPT
        )
        self.query_engine.update_prompts({"pandas_prompt": NEW_PROMPT})
        return self.query_engine

    def build_tools(self):
        if self.query_engine is None:
            self.build_query_engine()
        tools = [
            QueryEngineTool(
                query_engine=self.query_engine,
                metadata=ToolMetadata(
                    name="parse_stock_data",
                    description="Use this tool to query stock price data, calculate metrics, analyze trends, and get specific values from the stock dataframe. This tool is REQUIRED for any question about stock prices, volumes, or trends.",
                ),
            ),
        ]
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
