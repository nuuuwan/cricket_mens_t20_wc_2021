from utils import timex, tsv

ODDS_FILE = 'src/cricket_mens_t20_wc_2021/data/odds.csv'

STARTING_ODDS = {
    'IND': 0.31,
    'ENG': 0.19,
    'AUS': 0.12,
    'WI': 0.11,
    'NZ': 0.10,
    'PAK': 0.09,
    'SA': 0.03,
    'SL': 0.02,
    'BAN': 0.02,
    'AFG': 0.02,
    'SCO': 0.00,
    'NAM': 0.00,
}


# @cache(CACHE_NAME, CACHE_TIMEOUT)
def load_odds():
    def clean_row(d):
        team_1 = d['team_1']
        team_2 = d['team_2']
        if d['p1'] == '':
            s1 = STARTING_ODDS[team_1]
            s2 = STARTING_ODDS[team_2]
            p1 = (s1) / max(s1 + s2, 0.1)
        else:
            p1 = (float)(d['p1'])

        ut = timex.parse_time('2021-' + d['date'], '%Y-%d-%b')
        date_id = timex.get_date_id(ut)
        return {
            'match_no': (int)(d['\ufeffmatch_no']),
            'date_id': date_id,
            'team_1': team_1,
            'team_2': team_2,
            'p1': p1,
            'p2': 1 - p1,
        }

    return sorted(
        list(map(clean_row, tsv.read(ODDS_FILE, delimiter=','))),
        key=lambda x: x['match_no'],
    )


if __name__ == '__main__':
    for match in load_odds():
        print(match)
