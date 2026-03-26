#!/usr/bin/env python3
from urlmatch import urlmatch

import json
import os
import re
import unittest


NEVERMATCHES = "https://this-never-matches-but-should-never-throw.com"

KNOWN_ACTIONS = {
    "redirect",
    "regex-path",
    "regex-path-template",
    "base64,redirect",
}

REQUIRED_FIELDS = {"include", "exclude", "action", "param"}

REGEX_ACTIONS = {"regex-path", "regex-path-template"}


class DebounceTester(unittest.TestCase):
    def setUp(self):
        self.raw_debounce = self.readFile('debounce.json')
        self.rules_debounce = self.loadRules(self.raw_debounce)
        self.rules_cleanurls = self.loadRules(self.readFile('clean-urls.json'))

        js_api_rules = self.readFile('clean-urls-permissions.json')
        self.rules_cleanurlperms = js_api_rules['js_api']

    def readFile(self, filename):
        basedir = os.path.dirname(__file__)
        debounce_json = os.path.join(basedir, "..", "..",
                                     "brave-lists", filename)
        with open(debounce_json) as fd:
            debounce_raw = json.load(fd)

        return debounce_raw

    def loadRules(self, raw_rules):
        rules = []
        for ruleset in raw_rules:
            rules.extend(ruleset['include'])
            rules.extend(ruleset['exclude'])
        return rules

    def test_load_debounce_list_no_exceptions(self):
        self.assertFalse(
            any(
                (urlmatch(u, NEVERMATCHES) for u in self.rules_debounce)
            )
        )
        self.assertFalse(
            any(
                (urlmatch(u, NEVERMATCHES) for u in self.rules_cleanurls)
            )
        )
        self.assertFalse(
            any(
                (urlmatch(u, NEVERMATCHES) for u in self.rules_cleanurlperms)
            )
        )

    # Verify every rule has the minimum required fields: include, exclude,
    # action, and param.
    def test_required_fields_present(self):
        for i, rule in enumerate(self.raw_debounce):
            for field in REQUIRED_FIELDS:
                self.assertIn(
                    field, rule,
                    f"Rule {i} is missing required field '{field}'"
                )

    # Catch typos in the action field by checking against the set of action
    # types supported by brave-core.
    def test_action_types_are_known(self):
        for i, rule in enumerate(self.raw_debounce):
            self.assertIn(
                rule['action'], KNOWN_ACTIONS,
                f"Rule {i} has unknown action '{rule['action']}'"
            )

    # For regex-path and regex-path-template rules, verify that the param
    # field compiles as a valid regular expression.
    def test_regex_param_is_valid(self):
        for i, rule in enumerate(self.raw_debounce):
            if rule['action'] in REGEX_ACTIONS:
                try:
                    re.compile(rule['param'])
                except re.error as e:
                    self.fail(
                        f"Rule {i} has invalid regex in param: {e}"
                    )

    # regex-path-template rules must have a redirect_url_template field,
    # otherwise brave-core has no template to substitute capture groups into.
    def test_regex_path_template_has_redirect_url_template(self):
        for i, rule in enumerate(self.raw_debounce):
            if rule['action'] == 'regex-path-template':
                self.assertIn(
                    'redirect_url_template', rule,
                    f"Rule {i} has action 'regex-path-template' but is "
                    f"missing 'redirect_url_template'"
                )

    # redirect_url_template is only meaningful on regex-path-template rules.
    # Its presence on other action types likely indicates a copy-paste error.
    def test_redirect_url_template_only_on_regex_path_template(self):
        for i, rule in enumerate(self.raw_debounce):
            if rule['action'] != 'regex-path-template':
                self.assertNotIn(
                    'redirect_url_template', rule,
                    f"Rule {i} has 'redirect_url_template' but action is "
                    f"'{rule['action']}', not 'regex-path-template'"
                )

    # A redirect_url_template without any $1..$9 placeholders would always
    # redirect to the same static URL, which is almost certainly a mistake.
    def test_redirect_url_template_has_placeholders(self):
        for i, rule in enumerate(self.raw_debounce):
            if rule.get('redirect_url_template'):
                self.assertRegex(
                    rule['redirect_url_template'], r'\$[1-9]',
                    f"Rule {i} has 'redirect_url_template' with no "
                    f"$1..$9 placeholders"
                )

    # Verify that $N placeholders in redirect_url_template don't reference
    # capture groups that don't exist in the param regex (e.g. $3 when the
    # regex only has 2 groups).
    def test_redirect_url_template_placeholders_match_capture_groups(self):
        for i, rule in enumerate(self.raw_debounce):
            if rule['action'] != 'regex-path-template':
                continue
            template = rule.get('redirect_url_template', '')
            placeholders = {int(m) for m in re.findall(r'\$([1-9])', template)}
            if not placeholders:
                continue
            num_groups = re.compile(rule['param']).groups
            max_placeholder = max(placeholders)
            self.assertLessEqual(
                max_placeholder, num_groups,
                f"Rule {i} template references ${max_placeholder} but "
                f"regex only has {num_groups} capture group(s)"
            )
