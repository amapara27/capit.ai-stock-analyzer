import argparse

from dotenv import load_dotenv

load_dotenv()


def cmd_report(args):
    from pulse.graph import build_report_graph
    graph = build_report_graph()
    if args.verbose:
        state = {}
        for update in graph.stream({}, stream_mode="updates"):
            for node, out in update.items():
                print(f"[{node}] -> {list(out.keys())}")
                state.update(out)
    else:
        state = graph.invoke({})
    print(f"Report written to {state['report_path']}")


def cmd_chat(args):
    from langgraph.checkpoint.memory import MemorySaver
    from pulse.graph import build_chat_agent

    agent = build_chat_agent(MemorySaver())
    config = {"configurable": {"thread_id": "cli"}}  # one thread = memory across turns
    print("Pulse chat — ask about your portfolio, stocks, or news (q to quit)")
    while True:
        try:
            prompt = input("\n> ")
        except EOFError:
            break
        if prompt.strip().lower() == "q":
            break
        for chunk, meta in agent.stream({"messages": [("user", prompt)]},
                                        config=config, stream_mode="messages"):
            if meta.get("langgraph_node") == "agent" and chunk.text():
                print(chunk.text(), end="", flush=True)
        print()


def cmd_chart(args):
    from pulse.config import DATA_DIR
    from pulse.stockdata import StockDataService
    service = StockDataService(DATA_DIR)
    df = service.get_historical_prices(args.years, tickers=[args.ticker])
    service.create_price_chart(df.xs(args.ticker, axis=1, level=1), args.ticker, args.years)


def main():
    parser = argparse.ArgumentParser(prog="pulse", description="Pulse Trading Assistant")
    sub = parser.add_subparsers(dest="command", required=True)

    p_report = sub.add_parser("report", help="Run the daily research pipeline")
    p_report.add_argument("--verbose", action="store_true", help="Stream per-node progress")
    p_report.set_defaults(func=cmd_report)

    p_chat = sub.add_parser("chat", help="Interactive analyst chat")
    p_chat.set_defaults(func=cmd_chat)

    p_chart = sub.add_parser("chart", help="Open an interactive price chart")
    p_chart.add_argument("ticker")
    p_chart.add_argument("--years", type=int, default=1)
    p_chart.set_defaults(func=cmd_chart)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
