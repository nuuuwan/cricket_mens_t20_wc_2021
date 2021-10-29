import statistics

from utils import timex

from cricket_mens_t20_wc_2021._constants import (
    N_MONTE,
    TEAM_TO_COLOR,
)
from cricket_mens_t20_wc_2021._utils import to_long_name
from cricket_mens_t20_wc_2021._infographicx import Infographic

CONFIDENCE = 0.9


def draw_chart_lineups(
    group_to_team_to_points_list,
    odds_index,
    single_odds_index,
    sorted_team_semi_p,
    sorted_team_final_p,
):
    infographic = Infographic()

    RADIUS = 0.01

    def draw_team_label(x, y_team, team, team_str):
        infographic.text(
            f'{team_str}',
            (x, y_team),
            ha='left',
            color='black',
        )
        infographic.circle(
            (x - RADIUS * 2, y_team),
            RADIUS,
            color=TEAM_TO_COLOR[team],
        )

    team_to_semi_p = dict(sorted_team_semi_p)
    team_to_final_p = dict(sorted_team_final_p)

    GROUP_PADDING = 0.15
    GROUP_HEIGHT = 1 - GROUP_PADDING * 2
    ITEM_HEIGHT = GROUP_HEIGHT * 0.5 / 7
    X_GROUP = 0.25
    semi_teams = []
    for group, team_to_points_list in group_to_team_to_points_list.items():
        i_group = (int)(group)
        y_group = GROUP_PADDING + 0.5 * GROUP_HEIGHT * (i_group - 1)
        group_str = str(group)
        if i_group == 1:
            group_str += '**'
        infographic.text(
            f'Group {group_str}',
            (X_GROUP, y_group),
            ha='left',
            color='gray',
            font_weight='bold',
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
            y_team = y_group + (1 + i_team) * ITEM_HEIGHT
            team_str = to_long_name(team)

            points_list = group_to_team_to_points_list[group][team]
            sorted_points_list = sorted(points_list)
            n = len(sorted_points_list)
            i_min = (int)(n * (1 - CONFIDENCE) / 2)
            i_max = (int)(n * (1 + CONFIDENCE) / 2)
            points_min = sorted_points_list[i_min]
            points_max = sorted_points_list[i_max]

            team_str += f' ({points_min} to {points_max})'
            draw_team_label(X_GROUP, y_team, team, team_str)

    SEMI_PADDING = 0.3
    SEMI_HEIGHT = 1 - SEMI_PADDING * 2
    X_SEMI = 0.5
    semi_to_teams = {
        1: [semi_teams[0], semi_teams[3]],
        2: [semi_teams[2], semi_teams[1]],
    }
    for semi, teams in semi_to_teams.items():
        i_semi = (int)(semi)
        y_semi = SEMI_PADDING + 0.5 * SEMI_HEIGHT * (i_semi - 1)
        semi_str = str(semi)
        if i_semi == 1:
            semi_str += '***'
        infographic.text(
            f'Semi-Final {semi_str}',
            (X_SEMI, y_semi),
            ha='left',
            color='gray',
            font_weight='bold',
        )

        for i_team, team in enumerate(teams):
            y_team = y_semi + (1 + i_team) * 0.35 / 7
            team_str = to_long_name(team)
            p = team_to_semi_p[team]
            team_str += f' ({p:.0%})'
            draw_team_label(X_SEMI, y_team, team, team_str)

    FINAL_PADDING = 0.4
    FINAL_HEIGHT = 1 - FINAL_PADDING * 2
    X_FINAL = 0.75
    i_final = 1
    y_final = FINAL_PADDING + 0.5 * FINAL_HEIGHT * (i_final - 1)
    infographic.text(
        'Final',
        (X_FINAL, y_final),
        ha='left',
        color='gray',
        font_weight='bold',
    )
    final_teams = [semi_teams[0], semi_teams[2]]
    for i_team, team in enumerate(final_teams):
        y_team = y_final + (1 + i_team) * 0.35 / 7
        team_str = to_long_name(team)
        p = team_to_final_p[team]
        team_str += f' ({p:.0%})'
        draw_team_label(X_FINAL, y_team, team, team_str)

    infographic.header('2021 ICC Men\'s T20 World Cup')
    date_str = timex.format_time(timex.get_unixtime(), '%b %d')
    infographic.subheader(f'Most Likely Outcomes* · {date_str}')

    infographic.supfooter(
        f'* Based on {N_MONTE:,} Monte Carlo Simulations'
        + ' and time-weighted history of match results',
    )

    # plt.annotate(
    #     f'** {CONFIDENCE:.0%} confidence intervals for group stage points',
    #     (0.35, 0.11),
    #
    #     ha='left',
    #     font_size=6,
    # )
    #
    # plt.annotate(
    #     '*** Probability of reaching stage',
    #     (0.35, 0.08),
    #
    #     ha='left',
    #     font_size=6,
    # )

    infographic.footer('Visualization & Analysis by @nuuuwan')
    infographic.save('/tmp/cricket_mens_t20_wc_2021.group_stage.png')
