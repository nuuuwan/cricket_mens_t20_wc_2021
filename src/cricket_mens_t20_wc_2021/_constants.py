"""Constants."""

N_MONTE = 1000
DPI_IMAGE_RESOLUTION = 600


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

GROUPS = [1, 2]

GROUP_1 = ['AUS', 'ENG', 'SA', 'WI', 'BAN', 'SL']
GROUP_2 = ['AFG', 'IND', 'NZ', 'PAK', 'SCO', 'NAM']
WC_TEAMS = GROUP_1 + GROUP_2

DIR_DATA = 'src/cricket_mens_t20_wc_2021/data'

TEAM_TO_COLOR = {
    'IND': '#1F399A',
    'ENG': '#FE0129',
    'AUS': '#E5E044',
    'WI': '#A13953',
    'NZ': '#14181B',
    'PAK': '#00A478',
    'SA': '#187C2B',
    'SL': '#000080',
    'BAN': '#015A48',
    'AFG': '#0664AE',
    'SCO': '#9F3BB4',
    'NAM': '#97DDFC',
}

WHITE_FORE_TEAMS = [
    'NZ',
    'IND',
    'SL',
]
