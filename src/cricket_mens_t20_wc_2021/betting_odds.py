import os
import statistics

from bs4 import BeautifulSoup
from utils import tsv, www

from cricket_mens_t20_wc_2021._constants import DIR_DATA, WC_TEAMS
from cricket_mens_t20_wc_2021._utils import long_to_short_name
from cricket_mens_t20_wc_2021.charts.draw_chart_p_winning import (
    draw_chart_p_winning,
)

ODDS_CHECKER_URL = 'https://www.oddschecker.com/cricket/t20-world-cup/winner'
BETTING_ODDS_FILE = os.path.join(DIR_DATA, 'betting_odds.tsv')


def store_latest_odds():
    html = www.read(ODDS_CHECKER_URL, use_selenium=True)
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', class_='eventTable')
    odds_data_list = []
    for tr in table.find_all('tr'):
        td_values = list(map(lambda td: td.text, tr.find_all('td')))
        team_long_name = td_values[0]
        team = long_to_short_name(team_long_name)
        if team in WC_TEAMS:
            q_list = []
            for td_value in td_values[1:]:
                if td_value == '':
                    continue
                if '/' in td_value:
                    n, d = td_value.split('/')
                    q = (int)(n) / (int)(d)
                else:
                    q = (int)(td_value)
                q_list.append(q)
            mean_q = statistics.mean(q_list)
            odds_data_list.append(
                {
                    'team': team,
                    'p_bet': 1 / mean_q,
                }
            )
    total_p = sum(list(map(lambda d: d['p_bet'], odds_data_list)))
    odds_data_list = sorted(
        list(
            map(
                lambda d: {
                    'team': d['team'],
                    'p': d['p_bet'] / total_p,
                },
                odds_data_list,
            )
        ),
        key=lambda d: -d['p'],
    )
    tsv.write(BETTING_ODDS_FILE, odds_data_list)


def load_latest_odds():
    return list(
        map(
            lambda d: {
                'team': d['team'],
                'p': (float)(d['p']),
            },
            tsv.read(BETTING_ODDS_FILE),
        )
    )


if __name__ == '__main__':
    store_latest_odds()
    sorted_team_winner_p = list(
        map(
            lambda d: [d['team'], d['p']],
            load_latest_odds(),
        )
    )
    print(sorted_team_winner_p)

    draw_chart_p_winning(
        {'': sorted_team_winner_p},
        'Winning - oddschecker.com',
        'winning.oddschecker',
    )
