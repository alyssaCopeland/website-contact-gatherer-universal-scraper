from typing import Dict, Iterable, List, Set
from urllib.parse import urljoin

from bs4 import BeautifulSoup

def _init_profile_map() -> Dict[str, Set[str]]:
    return {
        "facebook_profile": set(),
        "instagram_profile": set(),
        "linkedin_profile": set(),
        "twitter_x_profile": set(),
    }

def extract_social_profiles(html_pages: Iterable[str], base_url: str) -> Dict[str, Set[str]]:
    """
    Extract social profile links from HTML pages.

    Returns a mapping of:
    - facebook_profile
    - instagram_profile
    - linkedin_profile
    - twitter_x_profile
    """
    profiles = _init_profile_map()

    for html in html_pages:
        if not html:
            continue
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            href_lower = href.lower()
            absolute = urljoin(base_url, href)

            if "facebook.com" in href_lower:
                profiles["facebook_profile"].add(absolute)
            elif "instagram.com" in href_lower:
                profiles["instagram_profile"].add(absolute)
            elif "linkedin.com" in href_lower:
                profiles["linkedin_profile"].add(absolute)
            elif "twitter.com" in href_lower or "x.com" in href_lower:
                profiles["twitter_x_profile"].add(absolute)

    return profiles