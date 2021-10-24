import random

import matplotlib.pyplot as plt

from cricket_mens_t20_wc_2021._constants import GROUP_1, GROUP_2, TEAM_TO_COLOR
from cricket_mens_t20_wc_2021._utils import log, to_hashtag
from cricket_mens_t20_wc_2021.odds import (
    load_odds_historical_index,
    load_single_odds_historical_index,
)
from cricket_mens_t20_wc_2021.wc_agenda import load_agenda


def simulate_match(odds_index, single_odds_index, team_1, team_2):
    p1 = odds_index.get(team_1, {}).get(team_2, None)
    if p1 is None:
        p1 = single_odds_index[team_1] / (
            single_odds_index[team_1] + single_odds_index[team_2]
        )

    # HACK! Namibia
    if team_1 == 'NAM':
        return 2
    if team_2 == 'NAM':
        return 1
    if p1 > random.random():
        return 1
    else:
        return 2


def simulate_group_stage(odds_index, single_odds_index):
    match_list = load_agenda()
    outcomes = []
    for match in match_list:
        team_1 = match['team_1']
        team_2 = match['team_2']
        winner = match['winner']

        # if no winner, simulate
        if not winner:
            winner = simulate_match(
                odds_index, single_odds_index, team_1, team_2
            )

        outcome = {
            'team_1': team_1,
            'team_2': team_2,
            'winner': winner,
        }
        outcomes.append(outcome)
    return outcomes


def build_points_table(outcomes):
    team_to_points = {}
    for outcome in outcomes:
        team_1 = outcome['team_1']
        team_2 = outcome['team_2']
        winner = outcome['winner']
        if winner == 1:
            team_to_points[team_1] = team_to_points.get(team_1, 0) + 2
        else:
            team_to_points[team_2] = team_to_points.get(team_2, 0) + 2

    group_to_team_to_points = {}
    for group_id, group_teams in [
        [1, GROUP_1],
        [2, GROUP_2],
    ]:
        group_to_team_to_points[group_id] = {}
        for team in group_teams:
            group_to_team_to_points[group_id][team] = team_to_points.get(
                team, 0
            )
    return group_to_team_to_points


def get_semifinals_teams(group_to_team_to_points):
    def get_top2_teams(team_to_points):
        sorted_team_points = sorted(
            team_to_points.items(),
            key=lambda x: -x[1],
        )
        return [
            sorted_team_points[0][0],
            sorted_team_points[1][0],
        ]

    return get_top2_teams(group_to_team_to_points[1]) + get_top2_teams(
        group_to_team_to_points[2]
    )


def winner_to_team(team_1, team_2, winner):
    if winner == 1:
        return team_1
    if winner == 2:
        return team_2
    return 'No Result'


def simulate_knowckout_stage(odds_index, single_odds_index, semi_finals_teams):
    sf11, sf22, sf21, sf12 = semi_finals_teams
    winner_sf1 = simulate_match(odds_index, single_odds_index, sf11, sf12)
    winner_sf2 = simulate_match(odds_index, single_odds_index, sf21, sf22)

    f1 = winner_to_team(sf11, sf12, winner_sf1)
    f2 = winner_to_team(sf21, sf22, winner_sf2)

    winner_f = simulate_match(odds_index, single_odds_index, f1, f2)
    winning_team = winner_to_team(f1, f2, winner_f)
    return winning_team


def simulate_monte_carlo():
    odds_index = load_odds_historical_index()
    single_odds_index = load_single_odds_historical_index()
    N_MONTE = 10_000
    team_to_semi_n = {}
    team_to_winner_n = {}
    for m in range(0, N_MONTE):
        if m % 1_000 == 0:
            log.info(f'{m}/{N_MONTE} simulation')

        outcomes = simulate_group_stage(odds_index, single_odds_index)
        group_to_team_to_points = build_points_table(outcomes)
        semi_finals_teams = get_semifinals_teams(group_to_team_to_points)
        winner = simulate_knowckout_stage(
            odds_index, single_odds_index, semi_finals_teams
        )

        for team in semi_finals_teams:
            team_to_semi_n[team] = team_to_semi_n.get(team, 0) + 1
        team_to_winner_n[winner] = team_to_winner_n.get(winner, 0) + 1

    sorted_team_semi_p = list(
        map(
            lambda x: [x[0], x[1] / N_MONTE],
            sorted(team_to_semi_n.items(), key=lambda x: -x[1]),
        )
    )
    sorted_team_winner_p = list(
        map(
            lambda x: [x[0], x[1] / N_MONTE],
            sorted(team_to_winner_n.items(), key=lambda x: -x[1]),
        )
    )
    return sorted_team_semi_p, sorted_team_winner_p


def simulate_and_describe():
    sorted_team_semi_p, sorted_team_winner_p = simulate_monte_carlo()
    labels = []
    sizes = []
    colors = []
    others_size = 0
    for label, sorted_team_x_p in [
        ['P(Winning)', sorted_team_winner_p],
    ]:
        print('-' * 32)
        print(label)
        print('-' * 32)
        for team, p in sorted_team_x_p:
            hash_name = to_hashtag(team)
            print(f'{p:.0%} {hash_name}')

            if p > 0.025:
                labels.append(hash_name)
                sizes.append(p)
                colors.append(TEAM_TO_COLOR[team])
            else:
                others_size += p

        if others_size > 0:
            labels.append('')
            sizes.append(others_size)
            colors.append('gray')
        print('...')

    # build chart
    fig1, ax1 = plt.subplots()
    _, texts, auto_texts = ax1.pie(
        sizes,
        labels=labels,
        colors=colors,
        autopct='%1.0f%%',
        shadow=True, startangle=90,
    )
    for i, text in enumerate(texts):
        if text.get_text() == '#NewZealand':
            auto_texts[i].set_color('white')
    plt.show()


if __name__ == '__main__':
    simulate_and_describe()
