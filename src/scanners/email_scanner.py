import re
from typing import Iterable, Set, List

_EMAIL_REGEX = re.compile(
    r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+"
)

def extract_emails(html_pages: Iterable[str]) -> Set[str]:
    """
    Extract email addresses from an iterable of HTML page contents.
    """
    emails: Set[str] = set()
    for html in html_pages:
        if not html:
            continue
        found: List[str] = _EMAIL_REGEX.findall(html)
        for email in found:
            # Basic cleanup: strip trailing punctuation
            email = email.strip(".,;: )]>\"'")
            emails.add(email)
    return emails