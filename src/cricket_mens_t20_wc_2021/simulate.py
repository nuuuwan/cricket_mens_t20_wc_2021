import random

from cricket_mens_t20_wc_2021._constants import (GROUP_1, GROUP_2, GROUPS,
                                                 N_MONTE, WC_TEAMS)
from cricket_mens_t20_wc_2021._utils import get_group, log
from cricket_mens_t20_wc_2021.odds import get_p1
from cricket_mens_t20_wc_2021.wc_agenda import load_agenda

# plt.rcParams['font.sans-serif'] = "Arial"


def simulate_match(odds_index, single_odds_index, team_1, team_2):
    p1 = get_p1(odds_index, single_odds_index, team_1, team_2)

    # HACK! Namibia
    if random.random() < 0.90:
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
        date_id = match['date_id']
        match_no = match['match_no']
        team_1 = match['team_1']
        team_2 = match['team_2']
        winner = match['winner']

        # if no winner, simulate
        if not winner:
            winner = simulate_match(
                odds_index, single_odds_index, team_1, team_2
            )

        outcome = {
            'date_id': date_id,
            'match_no': match_no,
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
    P_TIE_BREAKER = 0.1

    def get_top2_teams(team_to_points):
        sorted_team_points = sorted(
            team_to_points.items(),
            key=lambda x: -x[1] + random.random() * P_TIE_BREAKER,
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


def simulate_knockout_stage(odds_index, single_odds_index, semi_finals_teams):
    sf11, sf22, sf21, sf12 = semi_finals_teams
    winner_sf1 = simulate_match(odds_index, single_odds_index, sf11, sf12)
    winner_sf2 = simulate_match(odds_index, single_odds_index, sf21, sf22)

    f1 = winner_to_team(sf11, sf12, winner_sf1)
    f2 = winner_to_team(sf21, sf22, winner_sf2)

    winner_f = simulate_match(odds_index, single_odds_index, f1, f2)
    winning_team = winner_to_team(f1, f2, winner_f)
    return [f1, f2], winning_team


def simulate_monte_carlo(odds_index, single_odds_index):
    team_to_semi_n = dict(list(map(lambda x: [x, 0], WC_TEAMS)))
    team_to_final_n = dict(list(map(lambda x: [x, 0], WC_TEAMS)))
    team_to_winner_n = dict(list(map(lambda x: [x, 0], WC_TEAMS)))
    group_to_team_to_total_points = {}
    outcomes_list = []
    semi_finals_teams_list = []
    group_to_team_to_points_list = {}

    for m in range(0, N_MONTE):
        if m % 1_000 == 0:
            log.info(f'{m}/{N_MONTE} simulation')

        outcomes = simulate_group_stage(odds_index, single_odds_index)
        outcomes_list.append(outcomes)
        group_to_team_to_points = build_points_table(outcomes)

        for group in GROUPS:
            if group not in group_to_team_to_total_points:
                group_to_team_to_total_points[group] = {}
                group_to_team_to_points_list[group] = {}

            for team, points in group_to_team_to_points[group].items():
                if team not in group_to_team_to_total_points[group]:
                    group_to_team_to_total_points[group][team] = 0
                    group_to_team_to_points_list[group][team] = []

                group_to_team_to_total_points[group][team] += points
                group_to_team_to_points_list[group][team].append(points)

        semi_finals_teams = get_semifinals_teams(group_to_team_to_points)
        semi_finals_teams_list.append(semi_finals_teams)

        final_teams, winner = simulate_knockout_stage(
            odds_index, single_odds_index, semi_finals_teams
        )

        for team in semi_finals_teams:
            team_to_semi_n[team] += 1

        for team in final_teams:
            team_to_final_n[team] += 1
        team_to_winner_n[winner] += 1

    sorted_team_semi_p = list(
        map(
            lambda x: [x[0], x[1] / N_MONTE],
            sorted(
                team_to_semi_n.items(),
                key=lambda x: -x[1] + get_group(x[0]) * N_MONTE * 10,
            ),
        )
    )

    sorted_team_final_p = list(
        map(
            lambda x: [x[0], x[1] / N_MONTE],
            sorted(
                team_to_final_n.items(),
                key=lambda x: -x[1] + get_group(x[0]) * N_MONTE * 10,
            ),
        )
    )

    sorted_team_winner_p = list(
        map(
            lambda x: [x[0], x[1] / N_MONTE],
            sorted(team_to_winner_n.items(), key=lambda x: -x[1]),
        )
    )

    return (
        sorted_team_semi_p,
        sorted_team_final_p,
        sorted_team_winner_p,
        outcomes_list,
        semi_finals_teams_list,
        group_to_team_to_points_list,
    )
