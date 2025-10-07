from dotenv import load_dotenv
load_dotenv()

import os
import pandas as pd
from llama_index.experimental.query_engine import PandasQueryEngine

from prompts import new_prompt, instruction_str
from prompts import context

from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.agent.workflow import AgentWorkflow

import asyncio
import logging

# Loads stock data
stock_path = os.path.join("data", "stock_data.csv")
stock_df = pd.read_csv(stock_path)


# Gives thoughts and detailed output - wrapping over df and giving interface to ask questions about population data
stock_query_engine = PandasQueryEngine(
    df = stock_df, verbose = True, instruction_str=instruction_str
)
stock_query_engine.update_prompts({"pandas_prompt": new_prompt})

# Define tools the agent can use: note_engine and a population query engine (with metadata for context)
tools = [
        # note_engine,
        QueryEngineTool(
            query_engine = stock_query_engine,
            metadata = ToolMetadata(
                name = "stock_data",
                description = "Use this tool to query stock price data, calculate metrics, analyze trends, and get specific values from the stock dataframe. This tool is REQUIRED for any question about stock prices, volumes, or trends.",
         ),
    ),
]

logging.getLogger("httpx").setLevel(logging.WARNING)

# Creates the agent using the llm and tools specified
llm = OpenAI(model="gpt-3.5-turbo")
agent = ReActAgent(tools=tools, llm=llm, verbose=True, context=context)

workflow = AgentWorkflow([agent])

# Declaring prompt - user input, q exits the loop - agent queries the prompt. Have to run asyncronously
async def main():
    while True:
        prompt = input("Enter a prompt (or q to quit): ")
        if prompt.lower() == 'q':
            break
        result = await workflow.run(prompt, max_iterations=30)
        print(result)

asyncio.run(main())
