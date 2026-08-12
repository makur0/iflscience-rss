import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

def generate_esesja_rss(output_filename="esesja_feed.xml"):
    # Target both the main page and posiedzenia list
    urls = [
        "https://podkowalesna.esesja.pl/",
        "https://podkowalesna.esesja.pl/posiedzenia"
    ]
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    fg = FeedGenerator()
    fg.title("Podkowa Leśna - Posiedzenia eSesja")
    fg.link(href="https://podkowalesna.esesja.pl/", rel="alternate")
    fg.description("RSS Feed - Posiedzenia i Sesje Rady Miasta Podkowa Leśna")
    fg.language("pl")

    seen_links = set()
    sessions_found = 0

    print("Fetching sessions from eSesja Podkowa Leśna...")
    
    for url in urls:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Look for session links containing '/posiedzenie/'
            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"]

                if href.startswith("/"):
                    href = "https://podkowalesna.esesja.pl" + href

                title = a_tag.get_text(strip=True)

                if "/posiedzenie/" in href and href not in seen_links and len(title) > 5:
                    seen_links.add(href)
                    sessions_found += 1

                    fe = fg.add_entry()
                    fe.id(href)
                    fe.title(title)
                    fe.link(href=href)
                    fe.description(title)
        except Exception as e:
            print(f"Warning: Failed to fetch {url}: {e}")

    fg.rss_file(output_filename)
    print(f"Done! Generated '{output_filename}' with {sessions_found} sessions.")

if __name__ == "__main__":
    generate_esesja_rss()
