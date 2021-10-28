import os
import statistics

import matplotlib.pyplot as plt
from utils import timex

from cricket_mens_t20_wc_2021._constants import (
    N_MONTE,
    TEAM_TO_COLOR,
    DPI_IMAGE_RESOLUTION,
)
from cricket_mens_t20_wc_2021._utils import to_long_name

CONFIDENCE = 0.9


def draw_chart_lineups(
    group_to_team_to_points_list,
    odds_index,
    single_odds_index,
    sorted_team_semi_p,
    sorted_team_final_p,
):
    fig = plt.gcf()
    fig.set_size_inches(8, 4.5)

    team_to_semi_p = dict(sorted_team_semi_p)
    team_to_final_p = dict(sorted_team_final_p)

    GROUP_PADDING = 0.15
    GROUP_HEIGHT = 1 - GROUP_PADDING * 2
    ITEM_HEIGHT = GROUP_HEIGHT * 0.5 / 7
    X_GROUP = 0.25
    RADIUS = 0.01
    circles = []
    semi_teams = []
    for group, team_to_points_list in group_to_team_to_points_list.items():
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

        team_to_points_mean = dict(
            sorted(
                list(
                    map(
                        lambda x: [x[0], statistics.mean(x[1])],
                        team_to_points_list.items(),
                    )
                ),
                key=lambda x: -x[1],
            )
        )
        semi_teams += list(team_to_points_mean.keys())[:2]

        for i_team, [team, points_mean] in enumerate(
            team_to_points_mean.items()
        ):
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

            plt.annotate(
                f'{team_str}',
                (X_GROUP, y_team),
                xycoords='figure fraction',
                ha='left',
                color='black',
                fontsize=7,
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
    semi_to_teams = {
        1: [semi_teams[0], semi_teams[3]],
        2: [semi_teams[2], semi_teams[1]],
    }
    for semi, teams in semi_to_teams.items():
        i_semi = (int)(semi)
        y_semi = (1 - SEMI_PADDING) - 0.5 * SEMI_HEIGHT * (i_semi - 1)
        semi_str = str(semi)
        if i_semi == 1:
            semi_str += '***'
        plt.annotate(
            f'Semi-Final {semi_str}',
            (X_SEMI, y_semi),
            xycoords='figure fraction',
            ha='left',
            fontsize=9,
            color='gray',
            fontweight='bold',
        )

        for i_team, team in enumerate(teams):
            y_team = y_semi - (1 + i_team) * 0.35 / 7
            team_str = to_long_name(team)
            p = team_to_semi_p[team]
            team_str += f' ({p:.0%})'

            plt.annotate(
                f'{team_str}',
                (X_SEMI, y_team),
                xycoords='figure fraction',
                ha='left',
                fontsize=7,
                color='black',
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
        fontweight='bold',
    )
    final_teams = [semi_teams[0], semi_teams[2]]
    for i_team, team in enumerate(final_teams):
        y_team = y_final - (1 + i_team) * 0.35 / 7
        team_str = to_long_name(team)
        p = team_to_final_p[team]
        team_str += f' ({p:.0%})'

        plt.annotate(
            f'{team_str}',
            (X_FINAL, y_team),
            xycoords='figure fraction',
            ha='left',
            fontsize=7,
            color='black',
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
        (0.35, 0.14),
        xycoords='figure fraction',
        ha='left',
        fontsize=6,
    )

    plt.annotate(
        f'** {CONFIDENCE:.0%} confidence intervals for group stage points',
        (0.35, 0.11),
        xycoords='figure fraction',
        ha='left',
        fontsize=6,
    )

    plt.annotate(
        '*** Probability of reaching stage',
        (0.35, 0.08),
        xycoords='figure fraction',
        ha='left',
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
