import os
import random
import json

import matplotlib.pyplot as plt

from utils import timex

from cricket_mens_t20_wc_2021._constants import (
    GROUP_1,
    GROUP_2,
    TEAM_TO_COLOR,
    WHITE_FORE_TEAMS,
    GROUPS,
)
from cricket_mens_t20_wc_2021._utils import log, to_long_name
from cricket_mens_t20_wc_2021.odds import (
    load_odds_historical_index,
    load_single_odds_historical_index,
)
from cricket_mens_t20_wc_2021.wc_agenda import load_agenda

N_MONTE = 10_000

DPI_IMAGE_RESOLUTION = 300

# plt.rcParams['font.sans-serif'] = "Arial"


def get_p1(odds_index, single_odds_index, team_1, team_2):
    p1 = odds_index.get(team_1, {}).get(team_2, None)
    if p1 is None:
        p1 = single_odds_index[team_1] / (
            single_odds_index[team_1] + single_odds_index[team_2]
        )
    return p1



def simulate_match(odds_index, single_odds_index, team_1, team_2):
    p1 = get_p1(odds_index, single_odds_index, team_1, team_2)

    # HACK! Namibia
    # if team_1 == 'NAM':
    #     return 2
    # if team_2 == 'NAM':
    #     return 1

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


def simulate_monte_carlo(odds_index,single_odds_index ):
    team_to_semi_n = {}
    team_to_winner_n = {}
    group_to_table_id_to_n = {}
    semi_to_table_id_to_n = {}
    final_table_id_to_n = {}
    group_to_team_to_total_points = {}

    for m in range(0, N_MONTE):
        if m % 1_000 == 0:
            log.info(f'{m}/{N_MONTE} simulation')

        outcomes = simulate_group_stage(odds_index, single_odds_index)
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


    group_to_team_to_avg_points =  dict(
        list(
            map(
                lambda x: [
                    x[0],
                    dict(list(map(
                        lambda y: [y[0], y[1] / N_MONTE],
                        sorted(
                            x[1].items(),
                            key=lambda x: -x[1],
                        ),
                    ))),
                ],
                group_to_team_to_total_points.items(),
            )
        )
    )

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
    )


def draw_chart_p_winning(sorted_team_winner_p):
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
            hash_name = to_long_name(team)
            print(f'{p:.0%} {hash_name}')

            if p > 0.05:
                labels.append(hash_name)
                sizes.append(p)
                colors.append(TEAM_TO_COLOR[team])
            else:
                others_size += p

        if others_size > 0:
            labels.append('All Others')
            sizes.append(others_size)
            colors.append('gray')
        print('...')

    fig = plt.gcf()
    fig.set_size_inches(8, 4.5)

    plt.annotate(
        'ICC Men\'s T20 World Cup - 2021',
        (0.5, 0.97),
        xycoords='figure fraction',
        ha='center',
        fontsize=9,
    )
    date_str = timex.format_time(timex.get_unixtime(), '%B %d, %Y')
    plt.annotate(
        f'Probability of Winning (as of {date_str})*',
        (0.5, 0.91),
        xycoords='figure fraction',
        ha='center',
        fontsize=15,
    )

    plt.annotate(
        f'* Based on {N_MONTE:,} Monte Carlo Simulations and time-weighted history of match results',
        (0.5, 0.09),
        xycoords='figure fraction',
        ha='center',
        fontsize=6,
    )

    plt.annotate(
        f'Visualization & Analysis by @nuuuwan',
        (0.5, 0.04),
        xycoords='figure fraction',
        ha='center',
        fontsize=9,
    )

    _, texts, auto_texts = plt.gca().pie(
        sizes,
        labels=labels,
        colors=colors,
        autopct='%1.0f%%',
        startangle=90,
        normalize=False,
    )
    for i, text in enumerate(texts):
        if text.get_text() in list(
            map(
                lambda team: to_long_name(team),
                WHITE_FORE_TEAMS,
            )
        ):
            auto_texts[i].set_color('white')

    image_file = '/tmp/cricket_mens_t20_wc_2021.pwin.png'
    fig.savefig(image_file, dpi=DPI_IMAGE_RESOLUTION)
    os.system(f'open -a firefox {image_file}')

    plt.close()


def draw_chart_lineups(
    group_to_team_to_avg_points,
    group_to_sorted_table_id_n,
    semi_to_sorted_table_id_n,
    sorted_final_table_id_n,
    odds_index,
    single_odds_index,
):
    fig = plt.gcf()
    plt.gca()
    fig.set_size_inches(8, 4.5)

    GROUP_PADDING = 0.15
    GROUP_HEIGHT = 1 - GROUP_PADDING * 2
    ITEM_HEIGHT = GROUP_HEIGHT * 0.5 / 7
    X_GROUP = 0.25
    RADIUS = 0.01
    circles = []
    for group, sorted_table_id_n in group_to_sorted_table_id_n.items():
        i_group = (int)(group)
        y_group = (1 - GROUP_PADDING) - 0.5 * GROUP_HEIGHT * (i_group - 1)
        plt.annotate(
            f'Group {group}',
            (X_GROUP, y_group),
            xycoords='figure fraction',
            ha='left',
            fontsize=9,
            color='gray',
            fontweight='bold',
        )
        sorted_table_id, _ = sorted_table_id_n[0]
        sorted_teams = json.loads(sorted_table_id)
        for i_team, team in enumerate(sorted_teams):
            y_team = y_group - (1 + i_team) * ITEM_HEIGHT
            team_str = to_long_name(team)
            avg_points = group_to_team_to_avg_points[group][team]

            team_str += f' ({avg_points:.1f} pts)'

            if i_team < 2:
                team_str += ' ✓'
                color = 'black'
            else:
                color = 'lightgray'
            plt.annotate(
                f'{team_str}',
                (X_GROUP, y_team),
                xycoords='figure fraction',
                ha='left',
                color=color,
                fontsize=9,
            )
            circles.append(
                plt.Circle(
                    (X_GROUP - RADIUS * 3, y_team + RADIUS),
                    RADIUS,
                    color=TEAM_TO_COLOR[team],
                    figure=fig,
                    transform=fig.transFigure,
                )
            )

    SEMI_PADDING = 0.3
    SEMI_HEIGHT = 1 - SEMI_PADDING * 2
    X_SEMI = 0.5
    for semi, sorted_table_id_n in semi_to_sorted_table_id_n.items():
        i_semi = (int)(semi)
        y_semi = (1 - SEMI_PADDING) - 0.5 * SEMI_HEIGHT * (i_semi - 1)
        plt.annotate(
            f'Semi-Final {semi}',
            (X_SEMI, y_semi),
            xycoords='figure fraction',
            ha='left',
            fontsize=9,
            color='gray',
            fontweight='bold',
        )
        sorted_table_id, _ = sorted_table_id_n[0]
        sorted_teams = json.loads(sorted_table_id)

        team_1, team_2 = sorted_teams
        p1 = get_p1(odds_index, single_odds_index, team_1, team_2)
        ps = [p1, 1 - p1]

        for i_team, team in enumerate(sorted_teams):
            y_team = y_semi - (1 + i_team) * 0.35 / 7
            team_str = to_long_name(team)
            p = ps[i_team]
            team_str += f' ({p:.0%})'

            if p > 0.5:
                team_str += ' ✓'
                color = 'black'
            else:
                color = 'lightgray'
            plt.annotate(
                f'{team_str}',
                (X_SEMI, y_team),
                xycoords='figure fraction',
                ha='left',
                fontsize=9,
                color=color,
            )
            circles.append(
                plt.Circle(
                    (X_SEMI - RADIUS * 3, y_team + RADIUS),
                    RADIUS,
                    color=TEAM_TO_COLOR[team],
                    figure=fig,
                    transform=fig.transFigure,
                )
            )
    FINAL_PADDING = 0.4
    FINAL_HEIGHT = 1 - FINAL_PADDING * 2
    X_FINAL = 0.75
    i_final = 1
    y_final = (1 - FINAL_PADDING) - 0.5 * FINAL_HEIGHT * (i_final - 1)
    plt.annotate(
        'Final',
        (X_FINAL, y_final),
        xycoords='figure fraction',
        ha='left',
        fontsize=9,
        color='gray',
    )
    sorted_table_id, _ = sorted_final_table_id_n[0]
    sorted_teams = json.loads(sorted_table_id)

    team_1, team_2 = sorted_teams
    p1 = get_p1(odds_index, single_odds_index, team_1, team_2)
    ps = [p1, 1 - p1]

    for i_team, team in enumerate(sorted_teams):
        y_team = y_final - (1 + i_team) * 0.35 / 7
        team_str = to_long_name(team)
        p = ps[i_team]
        team_str += f' ({p:.0%})'

        if p > 0.5:
            team_str += ' ✓'
            color = 'black'
        else:
            color = 'lightgray'
        plt.annotate(
            f'{team_str}',
            (X_FINAL, y_team),
            xycoords='figure fraction',
            ha='left',
            fontsize=9,
            color=color,
        )
        circles.append(
            plt.Circle(
                (X_FINAL - RADIUS * 3, y_team + RADIUS),
                RADIUS,
                color=TEAM_TO_COLOR[team],
                figure=fig,
                transform=fig.transFigure,
            )
        )

    fig.patches.extend(circles)

    plt.annotate(
        'ICC Men\'s T20 World Cup - 2021',
        (0.5, 0.97),
        xycoords='figure fraction',
        ha='center',
        fontsize=9,
    )
    date_str = timex.format_time(timex.get_unixtime(), '%B %d, %Y')
    plt.annotate(
        f'Most Likely Outcomes (as of {date_str})*',
        (0.5, 0.91),
        xycoords='figure fraction',
        ha='center',
        fontsize=15,
    )

    plt.annotate(
        f'* Based on {N_MONTE:,} Monte Carlo Simulations and time-weighted history of match results',
        (0.5, 0.09),
        xycoords='figure fraction',
        ha='center',
        fontsize=6,
    )

    plt.annotate(
        f'Visualization & Analysis by @nuuuwan',
        (0.5, 0.04),
        xycoords='figure fraction',
        ha='center',
        fontsize=9,
    )

    plt.axis('off')

    image_file = '/tmp/cricket_mens_t20_wc_2021.lineup.png'
    fig.savefig(image_file, dpi=DPI_IMAGE_RESOLUTION)
    os.system(f'open -a firefox {image_file}')

    plt.close()


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
    ) = simulate_monte_carlo(
        odds_index,
        single_odds_index,
    )

    draw_chart_p_winning(sorted_team_winner_p)

    draw_chart_lineups(
        group_to_team_to_avg_points,
        group_to_sorted_table_id_n,
        semi_to_sorted_table_id_n,
        sorted_final_table_id_n,
        odds_index,
        single_odds_index,
    )
