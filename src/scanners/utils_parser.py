import logging
from typing import List, Set
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger("parser")

def fetch_page(url: str, timeout: int, headers: dict | None = None) -> str | None:
    try:
        resp = requests.get(url, timeout=timeout, headers=headers)
        resp.raise_for_status()
        logger.debug("Fetched URL: %s (status %s)", url, resp.status_code)
        return resp.text
    except Exception as exc:
        logger.warning("Failed to fetch URL '%s': %s", url, exc)
        return None

def _is_same_domain(url: str, base_netloc: str) -> bool:
    parsed = urlparse(url)
    if not parsed.netloc:
        return True
    return parsed.netloc == base_netloc

def _extract_links(base_url: str, html: str) -> List[str]:
    soup = BeautifulSoup(html, "html.parser")
    links: List[str] = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        joined = urljoin(base_url, href)
        links.append(joined)
    return links

def crawl_website(
    base_url: str,
    max_pages: int = 5,
    timeout: int = 10,
    user_agent: str | None = None,
) -> List[str]:
    """
    Crawl up to `max_pages` pages starting from `base_url`,
    restricted to the same domain. Returns a list of HTML page contents.
    """
    headers = {"User-Agent": user_agent} if user_agent else None

    parsed_base = urlparse(base_url)
    base_netloc = parsed_base.netloc

    visited: Set[str] = set()
    queue: List[str] = [base_url]
    pages_html: List[str] = []

    while queue and len(visited) < max_pages:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)

        html = fetch_page(url, timeout=timeout, headers=headers)
        if not html:
            continue
        pages_html.append(html)

        try:
            links = _extract_links(url, html)
        except Exception as exc:
            logger.debug("Error extracting links from '%s': %s", url, exc)
            continue

        for link in links:
            if len(visited) + len(queue) >= max_pages:
                break
            if _is_same_domain(link, base_netloc) and link not in visited and link not in queue:
                # Prioritize pages that look like contact/about pages
                if any(keyword in link.lower() for keyword in ("contact", "about", "support", "impressum")):
                    queue.insert(0, link)
                else:
                    queue.append(link)

    logger.info("Crawled %d pages for base URL '%s'", len(pages_html), base_url)
    return pages_html