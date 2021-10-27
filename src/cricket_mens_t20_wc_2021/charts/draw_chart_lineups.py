import json
import os

import matplotlib.pyplot as plt
from utils import timex

from cricket_mens_t20_wc_2021._constants import TEAM_TO_COLOR
from cricket_mens_t20_wc_2021._utils import to_long_name
from cricket_mens_t20_wc_2021.odds import get_p1

N_MONTE = 100_000

DPI_IMAGE_RESOLUTION = 600
CONFIDENCE = 0.9


def draw_chart_lineups(
    group_to_team_to_points_list,
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
        group_str = str(group)
        if i_group == 1:
            group_str += '**'
        plt.annotate(
            f'Group {group_str}',
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

            points_list = group_to_team_to_points_list[group][team]
            sorted_points_list = sorted(points_list)
            n = len(sorted_points_list)
            i_min = (int)(n * (1 - CONFIDENCE) / 2)
            i_max = (int)(n * (1 + CONFIDENCE) / 2)
            points_min = sorted_points_list[i_min]
            points_max = sorted_points_list[i_max]

            team_str += f' ({points_min} to {points_max})'

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
        '2021 ICC Men\'s T20 World Cup',
        (0.5, 0.97),
        xycoords='figure fraction',
        ha='center',
        fontsize=9,
    )
    date_str = timex.format_time(timex.get_unixtime(), '%b %d')
    plt.annotate(
        f'Most Likely Outcomes* · {date_str}',
        (0.5, 0.91),
        xycoords='figure fraction',
        ha='center',
        fontsize=15,
    )

    plt.annotate(
        f'* Based on {N_MONTE:,} Monte Carlo Simulations'
        + ' and time-weighted history of match results',
        (0.5, 0.11),
        xycoords='figure fraction',
        ha='center',
        fontsize=6,
    )

    plt.annotate(
        f'** Group Stage points are {CONFIDENCE:.0%} confidence intervals',
        (0.5, 0.08),
        xycoords='figure fraction',
        ha='center',
        fontsize=6,
    )

    plt.annotate(
        'Visualization & Analysis by @nuuuwan',
        (0.5, 0.04),
        xycoords='figure fraction',
        ha='center',
        fontsize=9,
    )

    plt.axis('off')

    image_file = '/tmp/cricket_mens_t20_wc_2021.group_stage.png'
    fig.savefig(image_file, dpi=DPI_IMAGE_RESOLUTION)
    os.system(f'open -a firefox {image_file}')

    plt.close()
