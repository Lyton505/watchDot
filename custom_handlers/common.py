from urllib.parse import urlparse
import re
import tldextract
import unicodedata

TERMS = ["staff ai research engineer", "intern", "head of duolingo english test"]

SEP = r"[ \t\r\n\u00A0\u202F\u2007\u2009\u2002\u2003\u2004\u2005\u2006\u205F\u3000\-–—·•|/]+"


# one translate table, faster than chained replaces
_TO_SPACE = dict.fromkeys(
    map(
        ord,
        [
            "\u00a0",  # NBSP
            "\u202f",  # narrow NBSP
            "\u2007",  # figure space
            "\u2009",  # thin space
            "\u2002",  # en space
            "\u2003",  # em space
            "\u2004",
            "\u2005",
            "\u2006",  # 3/4/6-em spaces
            "\u205f",  # medium math space
            "\u3000",  # ideographic space
        ],
    ),
    " ",
)

_REMOVE = dict.fromkeys(
    map(
        ord,
        [
            "\u200b",  # zero-width space
            "\u200c",  # ZWNJ
            "\u200d",  # ZWJ
            "\u2060",  # word joiner
        ],
    ),
    None,
)


def _normalize(text: str) -> str:
    # compatibility normalize (folds full-width letters/digits etc.)
    t = unicodedata.normalize("NFKC", text)
    # replace exotic spaces with normal space
    t = t.translate(_TO_SPACE)
    # drop zero-widths
    t = t.translate(_REMOVE)
    # collapse runs of whitespace
    t = re.sub(r"\s+", " ", t)
    return t


def compile_term(term: str) -> re.Pattern:
    tokens = term.split()
    pat = r"\b" + SEP.join(map(re.escape, tokens)) + r"\b"
    return re.compile(pat, re.I)


PATTERNS = [compile_term(t) for t in TERMS]


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

    normalized_text = _normalize(text)

    matches = []
    for term, pattern in zip(TERMS, PATTERNS):
        match = pattern.search(normalized_text)
        if match:
            # print(f"Pattern found: {match.group()} for term '{term}' in text.")
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
