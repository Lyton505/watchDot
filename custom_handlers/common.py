from urllib.parse import urlparse

import tldextract


def extract_root_domain_v2(url: str) -> str:
    netloc = urlparse(url).netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    return f"https://{netloc}"


def extract_root_domain(url: str) -> str:
    hostname = urlparse(url).hostname or ""
    ext = tldextract.extract(hostname)
    return f"{ext.domain}.{ext.suffix}"
