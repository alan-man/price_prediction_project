from scrapfly import ScrapeConfig, ScrapflyClient, ScrapeApiResponse
from typing import Dict, List
import asyncio
import json

SCRAPFLY = ScrapflyClient(key="scp-live-4d328964480446a88ccc0c9aaf04d521")

# scrapfly config
BASE_CONFIG = {
    # bypass web scraping blocking
    "asp": True,
    # set the proxy location to France
    "country": "fr",
}

def parse_search(result: ScrapeApiResponse):
    """parse search result data from nextjs cache"""
    # select the __NEXT_DATA__ script from the HTML
    next_data = result.selector.css("script[id='__NEXT_DATA__']::text").get()
    # extract ads listing data from the search page
    ads_data = json.loads(next_data)["props"]["pageProps"]["initialProps"]["searchData"]["ads"]
    return ads_data

async def scrape_search(url: str, max_pages: int) -> List[Dict]:
    """scrape leboncoin search"""
    print(f"scraping search {url}")
    first_page = await SCRAPFLY.async_scrape(ScrapeConfig(url, **BASE_CONFIG))
    search_data = parse_search(first_page)
    # add the ramaining pages in a scraping list
    _other_pages = [
        ScrapeConfig(f"{first_page.context['url']}&page={page}", **BASE_CONFIG)
        for page in range(2, max_pages + 1)        
    ]
    # scrape the remaining pages concurrently
    async for result in SCRAPFLY.concurrent_scrape(_other_pages):
        ads_data = parse_search(result)
        search_data.extend(ads_data)    
    print(json.dumps(search_data, indent=2))

# run the scraping search function
asyncio.run(scrape_search(url="https://www.leboncoin.fr/recherche?text=coffe", max_pages=2))

