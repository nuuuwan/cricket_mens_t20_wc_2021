from cricket_mens_t20_wc_2021._constants import WC_TEAMS
from cricket_mens_t20_wc_2021._utils import get_group
from cricket_mens_t20_wc_2021.charts.draw_chart_p_winning import (
    draw_chart_p_winning,
)


def draw_cut_on_outcome(outcomes_list, semi_finals_teams_list, match_no):
    n = len(outcomes_list)

    def get_split(outcomes):
        outcome = list(
            filter(
                lambda outcome: outcome['match_no'] == match_no,
                outcomes,
            )
        )[0]
        team_1 = outcome['team_1']
        team_2 = outcome['team_2']
        winner = outcome['winner']
        if winner == 1:
            return f'{team_1} Win'
        return f'{team_2} Win'

    splits = list(
        map(
            get_split,
            outcomes_list,
        )
    )

    split_to_team_to_semis_n = {}
    split_to_n = {}
    CURRENT_SPLIT = 'Pre-Match'
    for outcomes, semi_finals_teams, split0 in zip(
        outcomes_list, semi_finals_teams_list, splits
    ):
        for split in [split0, CURRENT_SPLIT]:
            if split not in split_to_team_to_semis_n:
                split_to_team_to_semis_n[split] = dict(
                    list(map(lambda x: [x, 0], WC_TEAMS))
                )
                split_to_n[split] = 0
            split_to_n[split] += 1

            for team in semi_finals_teams:
                split_to_team_to_semis_n[split][team] += 1

    split_to_sorted_team_semi_p = dict(
        list(
            map(
                lambda x: [
                    (
                        'If %s (P =%4.2g%%)'
                        % (x[0], split_to_n[x[0]] * 100.0 / n)
                    )
                    if (x[0] != CURRENT_SPLIT)
                    else CURRENT_SPLIT,
                    sorted(
                        list(
                            map(
                                lambda y: [y[0], y[1] / split_to_n[x[0]]],
                                x[1].items(),
                            )
                        ),
                        key=lambda y: -y[1] + get_group(y[0]) * 10,
                    ),
                ],
                split_to_team_to_semis_n.items(),
            )
        )
    )
    draw_chart_p_winning(
        split_to_sorted_team_semi_p, 'Reaching the Semis', f'semis_{match_no}'
    )
