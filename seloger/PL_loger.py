from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio

SEARCH_URL = "https://www.leboncoin.fr/recherche?category=9&locations=Paris__48.86023250788424_2.339006433295173_9256&real_estate_type=1,2"

HEADERS = {
    ":authority":"api.leboncoin.fr",
    ":method":"POST",
    ":path":"/finder/search",
    ":scheme":"https",

    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "Cookie":"__Secure-Install=65e43f1d-fa8c-46b3-b55d-2242fd343d0b; cnfdVisitorId=27da7630-85ac-4abc-a92a-edbc0e70d8eb; include_in_experiment=false; _pcid=%7B%22browserId%22%3A%22mgjid1v8odtqw044%22%2C%22_t%22%3A%22mw7zfuwv%7Cmgjid7sv%22%7D; _pctx=%7Bu%7DN4IgrgzgpgThIC4B2YA2qA05owMoBcBDfSREQpAeyRCwgEt8oBJAE0RXSwH18yBbAO4B2AF4AzMIMEAffgHMAVvVbCIgkAF8gA; didomi_token=eyJ1c2VyX2lkIjoiMTk5Yzk1YjQtZjI2Yy02YzczLWI2NmMtYzZiMjg3MmM0YTUwIiwiY3JlYXRlZCI6IjIwMjUtMTAtMDlUMTQ6MjM6NDguNTE4WiIsInVwZGF0ZWQiOiIyMDI1LTEwLTEwVDE0OjIzOjU5LjgwNloiLCJ2ZW5kb3JzIjp7ImRpc2FibGVkIjpbImdvb2dsZSIsImM6cGludGVyZXN0IiwiYzpsYmNmcmFuY2UiLCJjOmRpZG9taSIsImM6aWduaXRpb25vLUxWQU1aZG5qIiwiYzpnb29nbGVhbmEtNFRYbkppZ1IiLCJjOnB1cnBvc2VsYS0zdzRaZktLRCIsImM6bTZwdWJsaWNpLXRYVFlETkFjIiwiYzphZmZpbGluZXQiLCJjOnNwb25nZWNlbGwtbnl5YkFLSDIiLCJjOnRpa3Rvay1yS0FZRGdiSCIsImM6emFub3gtYVlZejZ6VzQiLCJjOnByZWJpZG9yZy1IaWppcllkYiIsImM6bGJjZnJhbmNlLUh5M2tZTTlGIl19LCJwdXJwb3NlcyI6eyJkaXNhYmxlZCI6WyJleHBlcmllbmNldXRpbGlzYXRldXIiLCJtZXN1cmVhdWRpZW5jZSIsInBlcnNvbm5hbGlzYXRpb25tYXJrZXRpbmciLCJwcml4IiwiY29tcGFyYWlzby1ZM1p5M1VFeCIsImRldmljZV9jaGFyYWN0ZXJpc3RpY3MiLCJnZW9sb2NhdGlvbl9kYXRhIl19LCJ2ZW5kb3JzX2xpIjp7ImRpc2FibGVkIjpbImdvb2dsZSIsImM6cHVycG9zZWxhLTN3NFpmS0tEIl19LCJ2ZXJzaW9uIjoyLCJhYyI6IkFBQUEuQUFBQSJ9; euconsent-v2=CQZBc4AQZEv0AAHABBENB_FgAAAAAAAAAAAAAAAAAABigAMAAQXSGAAYAAgukQAAwABBdIAA.YAAAAAAAAAAA; ry_ry-l3b0nco_realytics=eyJpZCI6InJ5XzdDNjgzNjQ3LTZBNjAtNEQzQy1BNEIyLTQ4NEFFMEExNUE1NCIsImNpZCI6bnVsbCwiZXhwIjoxNzkxNTU3MTk1MDkzLCJjcyI6bnVsbH0%3D; adview_clickmeter=alu__listing__0__33d0cb10-16b9-4706-bb72-f723a9bbc49b; datadome=9vgMj0kSd2h~_J0RNZg8pOq2H9ec1dAEZG4HkmJrUhXh2WxHLLaVA5Xrkv~kc0CRTBYPZzTdvyfE2VVs7_~~iiPEUtNEXVBE~7T9p2unFp6bKznpKnNFoT2FbnqSleDN",
    "Content-Type": "application/json",
    "Api_key":"ba0c2dad52b3ec",
    "origin":"https://www.leboncoin.fr",
    "Accept":"*/*",
    "accept-encoding":"gzip, deflate, br, zstd",
    "accept-language":"en-US,en;q=0.9",
    "cache-control":"no-cache",
    "content-length":"333",
    "pragma":"no-cache",
    "priority":"u=1, i",
    "referer":"https://www.leboncoin.fr/recherche?category=9&locations=Paris__48.86023250788424_2.339006433295173_9256&real_estate_type=1,2",
    "sec-ch-ua":'Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "sec-ch-ua-mobile":"?0",
    "sec-ch-ua-platform":"Linux",
    "sec-fetch-dest":"empty",
    "sec-fetch-mode":"cors",
    "sec-fetch-site":"same-site",
    "x-lbc-experiment":"eyJ2ZXJzaW9uIjoxLCJyb2xsb3V0X3Zpc2l0b3JfaWQiOiIyN2RhNzYzMC04NWFjLTRhYmMtYTkyYS1lZGJjMGU3MGQ4ZWIifQ=="

}





async def get_listings_with_playwright():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(extra_http_headers=HEADERS)
        page = await context.new_page()
        await page.goto(SEARCH_URL, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_selector('ul[data-test-id="listing-column"]', timeout=30000)
        html = await page.content()
        await page.mouse.wheel(0, 1000)
        #await browser.close()

    soup = BeautifulSoup(html, "html.parser")
    container = soup.find("ul", {"data-test-id": "listing-column"})
    links = []
    if container:
        for li in container.find_all("li", class_="styles_adCard__JzKik"):
            a = li.find("a", href=True)
            if a:
                links.append("https://www.leboncoin.fr" + a["href"])
    return links


async def get_all_listing_urls(start_url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        urls = set()
        current_url = start_url

        while current_url:
            await page.goto(current_url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_selector('ul[data-test-id="listing-column"]', timeout=30000)
            soup = BeautifulSoup(await page.content(), "html.parser")

            container = soup.find("ul", {"data-test-id": "listing-column"})
            if container:
                for li in container.find_all("li", class_="styles_adCard__JzKik"):
                    a = li.find("a", href=True)
                    if a:
                        urls.add("https://www.leboncoin.fr" + a["href"])

            next_link = soup.find("a", {"rel": "next"})
            if next_link and next_link.get("href"):
                current_url = "https://www.leboncoin.fr" + next_link["href"]
            else:
                current_url = None

        return list(urls)



urls = asyncio.run(get_all_listing_urls(SEARCH_URL))
print(f"Found {len(urls)} listings")
print(urls)

