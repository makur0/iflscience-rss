import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import urllib3

# Suppress SSL warnings for TerazTeatr
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def generate_terazteatr_rss(output_filename="terazteatr_feed.xml"):
    url = "https://www.terazteatr.pl/aktualnosci"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "pl-PL,pl;q=0.9,en;q=0.8",
    }

    print("Fetching news from TerazTeatr...")
    fg = FeedGenerator()
    fg.title("TerazTeatr - Aktualności")
    fg.link(href="https://www.terazteatr.pl/aktualnosci", rel="alternate")
    fg.description("Aktualności teatralne z serwisu TerazTeatr.pl")
    fg.language("pl")

    seen_links = set()
    articles_found = 0

    try:
        # verify=False prevents SSL handshake failures on TerazTeatr
        response = requests.get(url, headers=headers, timeout=20, verify=False)
        response.raise_for_status()
        response.encoding = response.apparent_encoding or 'utf-8'

        soup = BeautifulSoup(response.text, "html.parser")

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]

            if href.startswith("/"):
                href = "https://www.terazteatr.pl" + href

            title = a_tag.get_text(strip=True)

            if (
                "/aktualnosci/" in href 
                and href not in seen_links 
                and len(title) > 5
                and not href.endswith("/aktualnosci")
            ):
                seen_links.add(href)
                articles_found += 1

                fe = fg.add_entry()
                fe.id(href)
                fe.title(title)
                fe.link(href=href)
                fe.description(title)

    except Exception as e:
        print(f"Warning/Error fetching TerazTeatr: {e}")

    # Fallback entry if no articles were extracted to prevent empty feed errors
    if articles_found == 0:
        fe = fg.add_entry()
        fe.id("https://www.terazteatr.pl/aktualnosci")
        fe.title("TerazTeatr - Aktualności")
        fe.link(href="https://www.terazteatr.pl/aktualnosci")
        fe.description("Odwiedź stronę TerazTeatr.pl, aby zobaczyć najnowsze artykuły.")

    fg.rss_file(output_filename)
    print(f"Done! Generated '{output_filename}' with {articles_found} articles.")

if __name__ == "__main__":
    generate_terazteatr_rss()
