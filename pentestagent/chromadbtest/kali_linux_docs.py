import time
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright

def extract_all_kali_links(base_url="https://www.kali.org/"):
    """Extract all internal Kali Linux links from the entire website homepage."""
    print(f"🌐 Scraping links from {base_url}")
    links = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(base_url, timeout=60000)
        page.wait_for_load_state('load')

        # Extract all anchor tags
        anchors = page.query_selector_all("a[href]")
        for anchor in anchors:
            href = anchor.get_attribute("href")
            if href:
                parsed = urlparse(href)
                if parsed.netloc == "" or parsed.netloc == urlparse(base_url).netloc:
                    # Relative URL or same domain
                    full_url = urljoin(base_url, href)
                    links.add(full_url)

        browser.close()

    print(f"✅ Found {len(links)} internal pages.")
    return list(links)

if __name__ == "__main__":
    kali_links = extract_all_kali_links()

    print("\n📄 List of links found:\n")
    for link in kali_links:
        print(link)

    print(f"\n🔢 Total links found: {len(kali_links)}")
