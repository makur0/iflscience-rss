import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import urllib3

# Suppress SSL warnings in case the site has strict/legacy SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def generate_rss(output_filename="IMDB_feed.xml"):
    url = "https://www.imdb.com/user/p.6zkvgpyeii72pau2ldg3lh3dgy/ratings/"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    fg = FeedGenerator()
    fg.title("Site Name - RSS")
    fg.link(href=url, rel="alternate")
    fg.description("RSS Feed for Site Name")
    fg.language("en")

    seen_links = set()
    articles_found = 0

    try:
        response = requests.get(url, headers=headers, timeout=20, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]

            # Fix relative links
            if href.startswith("/"):
                href = "https://EXAMPLE.COM" + href

            title = a_tag.get_text(strip=True)

            # ADJUST THIS FILTER to match article URLs on that specific site:
            if "article-keyword" in href and href not in seen_links and len(title) > 10:
                seen_links.add(href)
                articles_found += 1

                fe = fg.add_entry()
                fe.id(href)
                fe.title(title)
                fe.link(href=href)
                fe.description(title)

    except Exception as e:
        print(f"Error fetching site: {e}")

    # Fallback to prevent empty feed errors
    if articles_found == 0:
        fe = fg.add_entry()
        fe.id(url)
        fe.title("Site Name - RSS")
        fe.link(href=url)
        fe.description("Visit site directly.")

    fg.rss_file(output_filename)
    print(f"Done! Generated '{output_filename}' with {articles_found} articles.")

if __name__ == "__main__":
    generate_rss()
