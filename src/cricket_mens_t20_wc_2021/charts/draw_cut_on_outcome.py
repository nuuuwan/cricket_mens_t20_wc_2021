from cricket_mens_t20_wc_2021._constants import GROUP_1
from cricket_mens_t20_wc_2021.charts.draw_chart_p_winning import (
    draw_chart_p_winning,
)

from cricket_mens_t20_wc_2021._utils import log, get_group

def draw_cut_on_outcome(outcomes_list, semi_finals_teams_list):
    def get_split(outcomes):
        i_match = 6
        outcome = outcomes[i_match]
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
    for outcomes, semi_finals_teams, split in zip(
        outcomes_list, semi_finals_teams_list, splits
    ):
        if split not in split_to_team_to_semis_n:
            split_to_team_to_semis_n[split] = {}
            split_to_n[split] = 0
        split_to_n[split] += 1
        for team in semi_finals_teams:
            if team not in split_to_team_to_semis_n[split]:
                split_to_team_to_semis_n[split][team] = 0
            split_to_team_to_semis_n[split][team] += 1
    split_to_sorted_team_semi_p = dict(
        list(
            map(
                lambda x: [
                    x[0],
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
    print(split_to_sorted_team_semi_p)

    draw_chart_p_winning(split_to_sorted_team_semi_p, 'Reaching the Semis')
