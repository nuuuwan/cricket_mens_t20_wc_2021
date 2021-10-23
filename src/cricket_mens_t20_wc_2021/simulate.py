import random

from cricket_mens_t20_wc_2021._constants import GROUP_1, GROUP_2
from cricket_mens_t20_wc_2021._utils import to_hashtag
from cricket_mens_t20_wc_2021.odds import load_odds, STARTING_ODDS


def simulate():
    match_list = load_odds()
    outcomes = []
    for match in match_list:
        is_win1 = match['p1'] > random.random()
        p1 = 1 if is_win1 else 0
        outcome = {
            'team_1': match['team_1'],
            'team_2': match['team_2'],
            'p1': p1,
        }
        outcomes.append(outcome)
    return outcomes


def build_points_table(outcomes):
    team_to_points = {}
    for outcome in outcomes:
        team_1 = outcome['team_1']
        team_2 = outcome['team_2']
        p1 = outcome['p1']
        if p1 == 1:
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

def get_winning_team(semi_finals_teams):
    sf11, sf22, sf21, sf12 = semi_finals_teams

    def get_winner(t1, t2):
        s1 = STARTING_ODDS[t1]
        s2 = STARTING_ODDS[t2]
        p1 = s1 / (s1 + s2)
        is_win1 = (p1 > random.random())
        return t1 if (is_win1) else t2

    f1 = get_winner(sf11, sf12)
    f2 = get_winner(sf21, sf22)
    winner = get_winner(f1, f2)
    return winner




def simulate_monte_carlo():
    N_MONTE = 1000
    team_to_semi_n = {}
    team_to_winner_n = {}
    for m in range(0, N_MONTE):
        outcomes = simulate()
        group_to_team_to_points = build_points_table(outcomes)
        semi_finals_teams = get_semifinals_teams(group_to_team_to_points)
        winner = get_winning_team(semi_finals_teams)
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


if __name__ == '__main__':
    sorted_team_semi_p, sorted_team_winner_p = simulate_monte_carlo()
    for label, sorted_team_x_p in [
        ['P(Semi-Finals)', sorted_team_semi_p],
        ['P(Winning)', sorted_team_winner_p],
    ]:
        print('-' * 32)
        print(label)
        print('-' * 32)
        for team, p in sorted_team_x_p:
            hash_name = to_hashtag(team)
            print(f'{p:.0%} {hash_name}')
        print('...')
