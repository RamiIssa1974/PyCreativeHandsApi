# app/utils/strings.py
import re
import unicodedata

def to_valid_camel_case_file_name(name: str) -> str:
    """
    Equivalent to Helpers.ToValidCamelCaseFileName:
    - trim spaces
    - remove diacritics
    - keep letters/digits, replace separators with single '-'
    - camelCase-ish by collapsing spaces/separators
    - lowercase first char, remove leading/trailing dashes
    """
    if not name:
        return ""
    s = name.strip()

    # remove diacritics
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))

    # replace non-alnum with space
    s = re.sub(r"[^A-Za-z0-9]+", " ", s)
    parts = [p for p in s.split() if p]

    if not parts:
        return ""

    # camelCase-ish
    head = parts[0].lower()
    tail = [p[:1].upper() + p[1:] for p in parts[1:]]
    cc = head + "".join(tail)

    # safe fallback
    cc = re.sub(r"[^A-Za-z0-9_-]", "", cc)
    return cc[:128]  # keep within reasonable length
