#!/usr/bin/env python3
from urlmatch import urlmatch

import json
import os
import unittest


NEVERMATCHES = "https://this-never-matches-but-should-never-throw.com"


class DebounceTester(unittest.TestCase):
    def setUp(self):
        basedir = os.path.dirname(__file__)
        debounce_json = os.path.join(basedir, "..", "..",
                                     "brave-lists", "debounce.json")
        with open(debounce_json) as fd:
            debounce_raw = json.load(fd)

        rules = []
        for ruleset in debounce_raw:
            rules.extend(ruleset['include'])
            rules.extend(ruleset['exclude'])
        self.rules = rules

    def test_load_debounce_list_no_exceptions(self):
        self.assertFalse(
            any(
                (urlmatch(u, NEVERMATCHES) for u in self.rules)
            )
        )
