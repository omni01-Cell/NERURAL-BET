import asyncio

from dotenv import load_dotenv

from src.agents.dispatcher import DispatcherAgent

load_dotenv()


async def test_dispatcher():
    dispatcher = DispatcherAgent()

    test_queries = [
        "Arsenal vs Liverpool tonight",
        "Analysis of the Barcelona game",
        "Manchester match",  # Ambiguous
    ]

    print("--- Testing Dispatcher ---")
    for query in test_queries:
        print(f"\nQuery: {query}")
        result = await dispatcher.run(query)
        print(f"Match Found: {result.match_found}")
        if result.match_found:
            print(f"ID: {result.match_id}")
            print(f"Date: {result.date}")
        else:
            print(f"Reasoning: {result.reasoning}")


if __name__ == "__main__":
    asyncio.run(test_dispatcher())
