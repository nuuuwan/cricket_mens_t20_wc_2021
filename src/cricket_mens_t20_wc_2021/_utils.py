"""Utils."""

import logging

from cricket_mens_t20_wc_2021._constants import GROUP_1, SHORT_NAME_TO_NAME

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('cricket_mens_t20_wc_2021')

LONG_TO_SHORT_MAP = {}


def get_group(team):
    if team in GROUP_1:
        return 1
    return 2


def to_hashtag(short_name):
    return '#' + to_long_name(short_name).replace(' ', '')


def to_long_name(short_name):
    return SHORT_NAME_TO_NAME[short_name]


def long_to_short_name(long_name):
    if long_name not in LONG_TO_SHORT_MAP:
        words = long_name.split(' ')
        if len(words) == 1:
            short_name = long_name[:3].upper()
        else:
            short_name = ''.join(
                list(
                    map(
                        lambda word: word[0].upper(),
                        words,
                    )
                )
            )
        LONG_TO_SHORT_MAP[long_name] = short_name
    return LONG_TO_SHORT_MAP[long_name]
