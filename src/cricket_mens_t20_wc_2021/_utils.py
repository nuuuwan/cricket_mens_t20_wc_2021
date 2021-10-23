"""Utils."""

import logging

from cricket_mens_t20_wc_2021._constants import SHORT_NAME_TO_NAME

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('cricket_mens_t20_wc_2021')


def to_hashtag(short_name):
    return '#' + SHORT_NAME_TO_NAME[short_name].replace(' ', '')
