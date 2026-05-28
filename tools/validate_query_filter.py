#!/usr/bin/env python3

"""Validate that no parameters in brave-lists/query-filter.json overlap with
the keys of kConditionalQueryStringTrackers in brave-core's utils.cc.

Those parameters are stripped conditionally by brave-core (only when the URL
spec does NOT match a regex). Listing them in query-filter.json — where they
would always be stripped — defeats the conditional behavior.
"""

import json
import os
import re
import sys
import urllib.request


UTILS_URL = os.environ.get(
    "UTILS_URL",
    "https://raw.githubusercontent.com/brave/brave-core/refs/heads/master"
    "/components/query_filter/browser/utils.cc",
)
QUERY_FILTER = "brave-lists/query-filter.json"


def fetch_utils_cc(url):
    with urllib.request.urlopen(url) as resp:
        return resp.read().decode()


def extract_conditional_keys(source):
    """Return the sorted set of keys defined in kConditionalQueryStringTrackers.

    Entries in the source look like:  {"key", "value"},
    """
    # Slice from the variable's definition site (`name = ...`) to its
    # terminating `});`. Anchoring on `=` avoids matching comments or other
    # references to the variable name. Avoids running a full C++ parser and is
    # good enough for the compact format brave-core uses.
    match = re.search(r"\bkConditionalQueryStringTrackers\s*=", source)
    if match is None:
        return []
    start = match.end()
    end = source.find("});", start)
    if end == -1:
        return []
    block = source[start:end]
    return sorted(set(re.findall(r'\{\s*"([^"]+)"\s*,', block)))


def load_query_filter_params(path):
    with open(path) as fd:
        data = json.load(fd)
    params = set()
    for rule in data:
        params.update(rule.get("params", []))
    return params


def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    query_filter_path = os.path.join(repo_root, QUERY_FILTER)

    source = fetch_utils_cc(UTILS_URL)
    conditional_keys = extract_conditional_keys(source)

    if not conditional_keys:
        print(
            "::error::Failed to extract any keys from "
            "kConditionalQueryStringTrackers in utils.cc. "
            "Did the upstream source format change?"
        )
        return 1

    params = load_query_filter_params(query_filter_path)
    overlap = sorted(set(conditional_keys) & params)

    if overlap:
        print(
            "::error::query-filter.json contains parameter(s) also present "
            "in kConditionalQueryStringTrackers:"
        )
        for key in overlap:
            print(f"  - {key}")
        print(
            "\nbrave-core strips these conditionally (only when the URL "
            "spec does not match a regex)."
        )
        print(
            "Including them in query-filter.json would override that and "
            "strip them unconditionally."
        )
        print("Remove them from query-filter.json.")
        return 1

    print(
        "✅  query-filter.json contains no parameters overlapping with "
        "kConditionalQueryStringTrackers."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
