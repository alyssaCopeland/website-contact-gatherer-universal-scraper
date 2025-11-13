import re
from typing import Iterable, Set, List

# A simple, broad phone number pattern capturing international numbers.
_PHONE_REGEX = re.compile(
    r"""
    (?:
        \+?\d{1,3}[\s\-\.()]*
    )?
    (?:
        \d[\s\-\.()]*
    ){7,}
    """,
    re.VERBOSE,
)

def _normalize_phone(raw: str) -> str:
    # Keep digits and leading '+'
    raw = raw.strip()
    normalized = []
    for i, ch in enumerate(raw):
        if ch.isdigit():
            normalized.append(ch)
        elif ch == "+" and i == 0:
            normalized.append(ch)
    return "".join(normalized)

def extract_phone_numbers(html_pages: Iterable[str]) -> Set[str]:
    """
    Extract phone numbers from an iterable of HTML page contents.
    """
    phones: Set[str] = set()
    for html in html_pages:
        if not html:
            continue
        found: List[str] = _PHONE_REGEX.findall(html)
        for raw in found:
            phone = _normalize_phone(raw)
            if len(phone) >= 9:
                phones.add(phone)
    return phones