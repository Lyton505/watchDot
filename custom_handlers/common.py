from urllib.parse import urlparse
import re
import tldextract

TERMS = [
    "staff ai research engineer",
    "intern",
]

PATTERNS = [re.compile(rf"\b{re.escape(term)}\b", re.I) for term in TERMS]


def extract_root_domain_v2(url: str) -> str:
    netloc = urlparse(url).netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    return f"https://{netloc}"


def extract_root_domain(url: str) -> str:
    hostname = urlparse(url).hostname or ""
    ext = tldextract.extract(hostname)
    return f"{ext.domain}.{ext.suffix}"


async def search_terms(site, text) -> list[str]:
    """
    Search for job-related terms in the given text.
    """

    cleaned_site = extract_root_domain(site)
    cleaned_site_v2 = extract_root_domain_v2(site)

    matches = []
    for term, pattern in zip(TERMS, PATTERNS):
        if pattern.search(text):
            matches.append(term)
            if term == "intern":
                print(
                    f"\t[{cleaned_site}] Special term matched: {term} at {cleaned_site_v2}"
                )

    if matches:
        print(
            f"\t[{cleaned_site}] found match(es): {', '.join(matches)} at {cleaned_site_v2}\n"
        )
    else:
        print(f"\t[{cleaned_site}] found no matching jobs at {cleaned_site_v2}\n")

    return matches
