import re
from feedgen.feed import FeedGenerator
from playwright.sync_api import sync_playwright

IMDB_URL = "https://www.imdb.com/user/p.6zkvgpyeii72pau2ldg3lh3dgy/ratings/"
MAX_ITEMS_TO_CHECK = 25

def generate_imdb_rss(output_filename="imdb_feed.xml"):
    print("Fetching IMDb ratings with Playwright...")

    fg = FeedGenerator()
    fg.title("IMDb Ratings - malgorzata-kurowska")
    fg.link(href=IMDB_URL, rel="alternate")
    fg.description("Latest rated movies and TV shows by malgorzata-kurowska on IMDb")
    fg.language("en")

    items_found = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox"
            ]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="en-US"
        )
        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        try:
            page.goto(IMDB_URL, timeout=60000)

            # Dismiss Cookie Banner if it pops up
            try:
                page.locator("button[data-testid='accept-button'], #onetrust-accept-btn-handler").click(timeout=3000)
            except Exception:
                pass

            # Wait for list items to appear
            item_locator = page.locator("li.ipc-metadata-list-summary-item")
            item_locator.first.wait_for(state="visible", timeout=30000)

            total_found = item_locator.count()
            check_limit = min(total_found, MAX_ITEMS_TO_CHECK)

            for i in range(check_limit):
                item = item_locator.nth(i)

                # 1. Title & URL
                title_loc = item.locator("a.ipc-title-link-wrapper")
                if title_loc.count() == 0:
                    continue

                raw_title = title_loc.first.inner_text().strip()
                clean_title = re.sub(r'^\d+\.\s*', '', raw_title)

                href = title_loc.first.get_attribute("href")
                if not href or "/title/" not in href:
                    continue

                movie_id = href.split("/title/")[1].split("/")[0]
                movie_url = f"https://www.imdb.com/title/{movie_id}/"

                # 2. Extract User Rating
                user_rating_loc = item.locator(
                    "span.ipc-rating-star--user, "
                    "[data-testid='rating-button__user-rating'], "
                    ".ipc-rating-prompt__rating"
                )

                user_rating = "N/A"
                if user_rating_loc.count() > 0:
                    user_rating = user_rating_loc.first.inner_text().strip()
                else:
                    all_stars = item.locator("span.ipc-rating-star")
                    if all_stars.count() >= 2:
                        user_rating = all_stars.nth(1).inner_text().strip()
                    elif all_stars.count() == 1:
                        user_rating = all_stars.first.inner_text().strip()

                user_rating = user_rating.replace("\n", " ").replace("Rate", "").strip()
                if not user_rating:
                    user_rating = "N/A"

                feed_title = f"{clean_title} (Rating: {user_rating})" if user_rating != "N/A" else clean_title

                fe = fg.add_entry()
                fe.id(movie_url)
                fe.title(feed_title)
                fe.link(href=movie_url)
                fe.description(f"Title: {clean_title} | User Rating: {user_rating}")

                items_found += 1

        except Exception as e:
            print(f"Error scraping IMDb with Playwright: {e}")
        finally:
            browser.close()

    # Fallback entry
    if items_found == 0:
        fe = fg.add_entry()
        fe.id(IMDB_URL)
        fe.title("IMDb Ratings - malgorzata-kurowska")
        fe.link(href=IMDB_URL)
        fe.description("Visit IMDb to view ratings.")

    fg.rss_file(output_filename)
    print(f"Done! Generated '{output_filename}' with {items_found} items.")

if __name__ == "__main__":
    generate_imdb_rss()
