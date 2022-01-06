#!/usr/bin/env python3

"""Silly helper script to generate all the permutations of localhost aliases."""

LOCALHOST_ALIASES = [
    "localhost",
    "127.0.0.1",
    "[::1]",
    "[::ffff:7f00:1]",
]

NON_ROUTEABLE_ALIASES = [
    "0.0.0.0",
    "[::]",
    "[::ffff:0:0]",
]

def format_domain_filter(origins):
    prefix = "domain="
    origins_with_exception_indication = []
    for origin in origins:
        origins_with_exception_indication.append(f"~{origin}")
    return prefix + "|".join(origins_with_exception_indication)


def create_rule_for_alias(an_alias, all_aliases):
    all_other_aliases = all_aliases.copy()
    all_other_aliases.remove(an_alias)
    domain_filter = format_domain_filter(all_other_aliases)
    filter_rule = f"||{an_alias}^$third-party,{domain_filter}"
    return filter_rule

for alias_group in [NON_ROUTEABLE_ALIASES, LOCALHOST_ALIASES]:
    for alias in alias_group:
        print(create_rule_for_alias(alias, alias_group))