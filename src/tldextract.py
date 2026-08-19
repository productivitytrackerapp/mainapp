import os
from urllib.parse import urlparse

_LIST_PATH = os.path.join(os.path.dirname(__file__), "public_suffix_list.dat")
_PRIVATE_SECTION = "===BEGIN PRIVATE DOMAINS==="

_rules = set()
_exceptions = set()


def _load_rules():
    """Parse the ICANN part of the vendored list into normal and exception rules."""
    with open(_LIST_PATH, encoding="utf-8") as handle:
        for line in handle:
            rule = line.strip()
            if rule.startswith("//"):
                if _PRIVATE_SECTION in rule:
                    return
                continue
            if not rule:
                continue
            if rule.startswith("!"):
                _exceptions.add(rule[1:])
            else:
                _rules.add(rule)


_load_rules()


def _decode_label(label):
    """Turn a punycode label back into unicode, because the list stores unicode.

    Browsers hand back URLs in punycode form (``xn--1lqs03n.jp``) while the list
    spells the same suffix as ``京都.jp``, so without this they never match.
    """
    if not label.lower().startswith("xn--"):
        return label
    try:
        return label.encode("ascii").decode("idna")
    except (UnicodeError, ValueError):
        return label


def _suffix_label_count(labels):
    """Return how many trailing labels of ``labels`` form the public suffix."""
    # An exception rule beats every normal rule, so check those first.
    for index in range(len(labels)):
        if ".".join(labels[index:]) in _exceptions:
            return len(labels) - index - 1
    # Otherwise the longest matching rule wins; index 0 is the longest candidate.
    for index in range(len(labels)):
        if ".".join(labels[index:]) in _rules:
            return len(labels) - index
        if ".".join(["*"] + labels[index + 1:]) in _rules:
            return len(labels) - index
    # No rule matched at all, so the implicit "*" rule applies.
    return 1


def public_suffix(hostname):
    """Return the public suffix of ``hostname`` (e.g. ``co.uk`` for ``bbc.co.uk``)."""
    labels = hostname.split(".")
    # The list is lower case, so fold before matching; the returned labels keep
    # their original spelling.
    count = _suffix_label_count([_decode_label(label.lower()) for label in labels])
    return ".".join(labels[len(labels) - count:])


def domain_name(url):
    """Return the registrable domain of ``url``, or ``""`` if there isn't one."""
    if not url:
        return ""
    if "//" not in url:
        url = "//" + url
    try:
        hostname = urlparse(url).hostname
    except ValueError:
        return ""
    if not hostname:
        return ""
    hostname = hostname.strip(".")
    # An IP address has no registrable domain.
    if hostname.replace(".", "").isdigit() or ":" in hostname:
        return ""
    labels = hostname.split(".")
    # The list is lower case, so fold before matching; the returned labels keep
    # their original spelling.
    count = _suffix_label_count([_decode_label(label.lower()) for label in labels])
    if count >= len(labels):
        return ""
    return ".".join(labels[len(labels) - count - 1:])