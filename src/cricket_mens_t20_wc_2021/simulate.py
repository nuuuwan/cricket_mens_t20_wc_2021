import json
import random

from cricket_mens_t20_wc_2021._constants import GROUP_1, GROUP_2, GROUPS
from cricket_mens_t20_wc_2021._utils import log, get_group
from cricket_mens_t20_wc_2021.charts.draw_cut_on_outcome import (
    draw_cut_on_outcome,
)
from cricket_mens_t20_wc_2021.charts.draw_chart_p_winning import (
    draw_chart_p_winning,
)
from cricket_mens_t20_wc_2021.charts.draw_chart_lineups import (
    draw_chart_lineups,
)

draw_chart_lineups
from cricket_mens_t20_wc_2021.odds import (
    get_p1,
    load_odds_historical_index,
    load_single_odds_historical_index,
)
from cricket_mens_t20_wc_2021.wc_agenda import load_agenda

N_MONTE = 100_000

DPI_IMAGE_RESOLUTION = 600

# plt.rcParams['font.sans-serif'] = "Arial"


def simulate_match(odds_index, single_odds_index, team_1, team_2):
    p1 = get_p1(odds_index, single_odds_index, team_1, team_2)

    # HACK! Namibia
    if random.random() < 0.95:
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
    team_to_semi_n = {}
    team_to_winner_n = {}
    group_to_table_id_to_n = {}
    semi_to_table_id_to_n = {}
    final_table_id_to_n = {}
    group_to_team_to_total_points = {}
    outcomes_list = []
    semi_finals_teams_list = []

    for m in range(0, N_MONTE):
        if m % 1_000 == 0:
            log.info(f'{m}/{N_MONTE} simulation')

        outcomes = simulate_group_stage(odds_index, single_odds_index)
        outcomes_list.append(outcomes)
        group_to_team_to_points = build_points_table(outcomes)

        for group in GROUPS:
            sorted_teams = list(
                map(
                    lambda x: x[0],
                    sorted(
                        group_to_team_to_points[group].items(),
                        key=lambda x: -x[1],
                    ),
                )
            )
            if group not in group_to_table_id_to_n:
                group_to_table_id_to_n[group] = {}
            table_id = json.dumps(sorted_teams)
            if table_id not in group_to_table_id_to_n[group]:
                group_to_table_id_to_n[group][table_id] = 0
            group_to_table_id_to_n[group][table_id] += 1

            if group not in group_to_team_to_total_points:
                group_to_team_to_total_points[group] = {}

            for team, points in group_to_team_to_points[group].items():
                if team not in group_to_team_to_total_points[group]:
                    group_to_team_to_total_points[group][team] = 0
                group_to_team_to_total_points[group][team] += points

        semi_finals_teams = get_semifinals_teams(group_to_team_to_points)
        semi_finals_teams_list.append(semi_finals_teams)
        table_id1 = json.dumps([semi_finals_teams[0], semi_finals_teams[3]])
        table_id2 = json.dumps([semi_finals_teams[2], semi_finals_teams[1]])

        if '1' not in semi_to_table_id_to_n:
            semi_to_table_id_to_n = {'1': {}, '2': {}}
        if table_id1 not in semi_to_table_id_to_n['1']:
            semi_to_table_id_to_n['1'][table_id1] = 0
        semi_to_table_id_to_n['1'][table_id1] += 1
        if table_id2 not in semi_to_table_id_to_n['2']:
            semi_to_table_id_to_n['2'][table_id2] = 0
        semi_to_table_id_to_n['2'][table_id2] += 1

        final_teams, winner = simulate_knockout_stage(
            odds_index, single_odds_index, semi_finals_teams
        )

        table_id = json.dumps(final_teams)
        if table_id not in final_table_id_to_n:
            final_table_id_to_n[table_id] = 0
        final_table_id_to_n[table_id] += 1

        for team in semi_finals_teams:
            team_to_semi_n[team] = team_to_semi_n.get(team, 0) + 1
        team_to_winner_n[winner] = team_to_winner_n.get(winner, 0) + 1

    group_to_team_to_avg_points = dict(
        list(
            map(
                lambda x: [
                    x[0],
                    dict(
                        list(
                            map(
                                lambda y: [y[0], y[1] / N_MONTE],
                                sorted(
                                    x[1].items(),
                                    key=lambda x: -x[1],
                                ),
                            )
                        )
                    ),
                ],
                group_to_team_to_total_points.items(),
            )
        )
    )

    sorted_team_semi_p = list(
        map(
            lambda x: [x[0], x[1] / N_MONTE],
            sorted(team_to_semi_n.items(), key=lambda x: -x[1] + get_group(x[0]) * N_MONTE * 10),
        )
    )
    sorted_team_winner_p = list(
        map(
            lambda x: [x[0], x[1] / N_MONTE],
            sorted(team_to_winner_n.items(), key=lambda x: -x[1]),
        )
    )

    group_to_sorted_table_id_n = dict(
        list(
            map(
                lambda x: [
                    x[0],
                    sorted(
                        x[1].items(),
                        key=lambda x: -x[1],
                    ),
                ],
                group_to_table_id_to_n.items(),
            )
        )
    )

    semi_to_sorted_table_id_n = dict(
        list(
            map(
                lambda x: [
                    x[0],
                    sorted(
                        x[1].items(),
                        key=lambda x: -x[1],
                    ),
                ],
                semi_to_table_id_to_n.items(),
            )
        ),
    )

    sorted_final_table_id_n = sorted(
        final_table_id_to_n.items(),
        key=lambda x: -x[1],
    )

    return (
        group_to_team_to_avg_points,
        sorted_team_semi_p,
        sorted_team_winner_p,
        group_to_sorted_table_id_n,
        semi_to_sorted_table_id_n,
        sorted_final_table_id_n,
        outcomes_list,
        semi_finals_teams_list,
    )


if __name__ == '__main__':
    odds_index = load_odds_historical_index()
    single_odds_index = load_single_odds_historical_index()

    (
        group_to_team_to_avg_points,
        sorted_team_semi_p,
        sorted_team_winner_p,
        group_to_sorted_table_id_n,
        semi_to_sorted_table_id_n,
        sorted_final_table_id_n,
        outcomes_list,
        semi_finals_teams_list,
    ) = simulate_monte_carlo(
        odds_index,
        single_odds_index,
    )

    draw_chart_lineups(
        group_to_team_to_avg_points,
        group_to_sorted_table_id_n,
        semi_to_sorted_table_id_n,
        sorted_final_table_id_n,
        odds_index,
        single_odds_index,
    )

    draw_chart_p_winning({'': sorted_team_semi_p}, 'Reaching the Semis', 'semis')
    draw_chart_p_winning({'': sorted_team_winner_p}, 'Winning', 'winning')
    for i_match in [7, 8]:
        draw_cut_on_outcome(outcomes_list, semi_finals_teams_list, i_match)
