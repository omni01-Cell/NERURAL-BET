import asyncio
from src.providers.fbref_provider import FBRefProvider

async def main():
    provider = FBRefProvider()
    print("Attempting to fetch Liverpool stats via FBref...")
    result = await provider.get_team_form("Liverpool", league="PL")
    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
