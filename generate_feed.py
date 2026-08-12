import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

def generate_iflscience_rss(output_filename="iflscience_feed.xml"):
    url = "https://www.iflscience.com/latest"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    print("Fetching articles from IFLScience...")
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    fg = FeedGenerator()
    fg.title("IFLScience - Latest Articles")
    fg.link(href="https://www.iflscience.com/latest", rel="alternate")
    fg.description("Custom RSS Feed generated via Python & GitHub Actions")
    fg.language("en")

    seen_links = set()
    articles_found = 0

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]

        if href.startswith("/"):
            href = "https://www.iflscience.com" + href

        title = a_tag.get_text(strip=True)

        if (
            "iflscience.com/" in href 
            and href not in seen_links 
            and len(title) > 20
            and not href.endswith(("/latest", "/tags", "/privacy-policy"))
        ):
            last_part = href.split("-")[-1]
            if last_part.isdigit():
                seen_links.add(href)
                articles_found += 1

                fe = fg.add_entry()
                fe.id(href)
                fe.title(title)
                fe.link(href=href)
                fe.description(title)

    fg.rss_file(output_filename)
    print(f"Done! Generated '{output_filename}' with {articles_found} articles.")

if __name__ == "__main__":
    generate_iflscience_rss()
