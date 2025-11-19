from llama_index.core import PromptTemplate

# Tells agent what do with pandas df and how to respond
instruction_str = """\
    1. Convert the query to executable Python code using Pandas.
    2. The final line of code should be a Python expression that can be called with the `eval()` function.
    3. The code should represent a solution to the query.
    4. PRINT ONLY THE EXPRESSION.
    5. Do not quote the expression.
    6. Do not use statements like assignments (=) or imports. Only use expressions that return a value.
    7. The dataframe is already loaded as `df`. Do not try to read CSV files."""

# Specify context for agent to know what data it is working with - templating what we want prompt to look like
new_prompt = PromptTemplate(
    """\
    You are working with a pandas dataframe in Python.
    The name of the dataframe is `df`.
    This is the result of `print(df.head())`:
    {df_str}

    Follow these instructions:
    {instruction_str}
    Query: {query_str}

    Examples of valid expressions:
    - df['Close'].mean()
    - df[df['Volume'] > 1000000]
    - df.describe()
    - df['Close'].iloc[-1]

    Expression: """
)

# Context for agent to know what it is working with
context = """Purpose: The primary role of this agent is to assist users who are aiming to be informed on different 
            stocks in the stock market. They want to know the price action of the stock and different metrics. 
            
            IMPORTANT: 
            - You MUST use the stock_data tool to query the actual data before answering questions about stock prices, trends, or metrics.
            - You can ONLY analyze historical data. You CANNOT predict future prices or guarantee profits.
            - For questions about future performance or whether to buy/sell, analyze historical trends and patterns, 
              but clearly state that you cannot predict the future and this is not financial advice.
            - If a question requires real-time news or sentiment data that you don't have, acknowledge this limitation."""
