import os
from cricket_mens_t20_wc_2021.historical import (
    scrape_matches,
)

from cricket_mens_t20_wc_2021.betting_odds import (
    store_latest_odds,
    load_latest_odds,
)

from cricket_mens_t20_wc_2021.odds import (
    store_odds_historical,
    load_odds_historical_index,
    load_single_odds_historical_index,
)
from cricket_mens_t20_wc_2021.wc_agenda import (
    get_todays_matches,
    get_yesterdays_matches,
)

from cricket_mens_t20_wc_2021.simulate import simulate_monte_carlo

from cricket_mens_t20_wc_2021.charts.draw_chart_lineups import (
    draw_chart_lineups,
)
from cricket_mens_t20_wc_2021.charts.draw_chart_p_winning import (
    draw_chart_p_winning,
)
from cricket_mens_t20_wc_2021.charts.draw_cut_on_outcome import (
    draw_cut_on_outcome,
)

from cricket_mens_t20_wc_2021.charts.draw_single_team_path import (
    draw_single_team_path,
)


def run():
    # cleanup
    os.system('rm -rf /tmp/cricket_mens_t20_wc_2021.*.png')

    # historical
    scrape_matches()

    # odds
    store_odds_historical()
    odds_index = load_odds_historical_index()
    single_odds_index = load_single_odds_historical_index()

    # betting odds
    store_latest_odds()
    sorted_team_winner_oddschecker_p = list(
        map(
            lambda d: [d['team'], d['p']],
            load_latest_odds(),
        )
    )

    # simulate
    (
        sorted_team_semi_p,
        sorted_team_final_p,
        sorted_team_winner_p,
        outcomes_list,
        semi_finals_teams_list,
        group_to_team_to_points_list,
    ) = simulate_monte_carlo(
        odds_index,
        single_odds_index,
    )

    # charts
    draw_chart_lineups(
        group_to_team_to_points_list,
        odds_index,
        single_odds_index,
        sorted_team_semi_p,
        sorted_team_final_p,
    )

    draw_chart_p_winning(
        {'': sorted_team_semi_p}, 'Reaching the Semis', 'semis'
    )
    draw_chart_p_winning({'': sorted_team_winner_p}, 'Winning', 'winning')
    for match in get_todays_matches():
        match_no = match['match_no']
        draw_cut_on_outcome(outcomes_list, semi_finals_teams_list, match_no)

    for match in get_yesterdays_matches():
        for team in [match['team_1'], match['team_2']]:
            draw_single_team_path(team, outcomes_list, semi_finals_teams_list)

    draw_chart_p_winning(
        {'': sorted_team_winner_oddschecker_p},
        'Winning - oddschecker.com',
        'winning.oddschecker',
    )

    # after
    os.system('open -a preview /tmp/cricket_mens_t20_wc_2021.*.png')


if __name__ == '__main__':
    run()
