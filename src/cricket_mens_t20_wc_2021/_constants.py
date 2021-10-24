"""Constants."""

CACHE_NAME = 'cricket_mens_t20_wc_2021'
CACHE_TIMEOUT = 3600

SHORT_NAME_TO_NAME = {
    'IND': 'India',
    'ENG': 'England',
    'AUS': 'Australia',
    'WI': 'West Indies',
    'NZ': 'New Zealand',
    'PAK': 'Pakistan',
    'SA': 'South Africa',
    'SL': 'Sri Lanka',
    'BAN': 'Bangladesh',
    'AFG': 'Afghanistan',
    'SCO': 'Scotland',
    'NAM': 'Namibia',
}

GROUP_1 = ['AUS', 'ENG', 'SA', 'WI', 'BAN', 'SL']
GROUP_2 = ['AFG', 'IND', 'NZ', 'PAK', 'SCO', 'NAM']
WC_TEAMS = GROUP_1 + GROUP_2

DIR_DATA = 'src/cricket_mens_t20_wc_2021/data'
