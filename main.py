import sys

if __name__ == "__main__":
    if "scraper" in sys.argv:
        import asyncio
        from scraper.main import scraper_main
        asyncio.run(scraper_main())
    elif "api" in sys.argv:
        pass