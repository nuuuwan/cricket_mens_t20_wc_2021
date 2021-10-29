from utils import timex

from cricket_mens_t20_wc_2021._constants import N_MONTE
from cricket_mens_t20_wc_2021._utils import to_long_name
from cricket_mens_t20_wc_2021._infographicx import Infographic

CHAR_WIN = '✓'
CHAR_NOT_SURE = '?'
CHAR_LOSE = '✗'
STR_GAP = ';'


def get_wins(complete_result_id):
    return complete_result_id.count(CHAR_WIN)


def draw_single_team_path(team_0, outcomes_list, semi_finals_teams_list):
    n = len(outcomes_list)
    complete_result_id_to_n = {}
    complete_result_id_to_n_semis = {}
    date_id_today = timex.get_date_id()
    oppo_list = []
    is_oppo_done = False
    for outcomes, semi_finals_teams in zip(
        outcomes_list, semi_finals_teams_list
    ):
        result_str_list = []
        for match in outcomes:
            date_id = match['date_id']
            if date_id < date_id_today:
                continue
            team_1 = match['team_1']
            team_2 = match['team_2']
            winner = match['winner']
            result_str = None
            if team_0 == team_1:
                if winner == 1:
                    result_str = CHAR_WIN
                elif winner == 2:
                    result_str = CHAR_LOSE
                if not is_oppo_done:
                    oppo_list.append(team_2)
            elif team_0 == team_2:
                if winner == 1:
                    result_str = CHAR_LOSE
                elif winner == 2:
                    result_str = CHAR_WIN
                if not is_oppo_done:
                    oppo_list.append(team_1)

            if result_str:
                result_str_list.append(result_str)

        complete_result_id = STR_GAP.join(result_str_list)
        is_qualified = team_0 in semi_finals_teams

        if complete_result_id not in complete_result_id_to_n:
            complete_result_id_to_n[complete_result_id] = 0
            complete_result_id_to_n_semis[complete_result_id] = 0

        complete_result_id_to_n[complete_result_id] += 1
        if is_qualified:
            complete_result_id_to_n_semis[complete_result_id] += 1

        is_oppo_done = True

    complete_result_id_to_p_semis = dict(
        list(
            map(
                lambda x: [x[0], x[1] / complete_result_id_to_n[x[0]]],
                complete_result_id_to_n_semis.items(),
            )
        )
    )

    # view ----------------------------------------------------------------

    infographic = Infographic()

    p_cum = 0
    EPSILON = 0.0000001
    prev_n_wins = None

    x_offset = 0.3
    n_lines = len(complete_result_id_to_p_semis.keys()) + 7
    n_oppos = len(oppo_list)
    col_width = 0.09
    line_height = 1 / n_lines
    font_size = 7
    sorted_id_and_p = sorted(
        complete_result_id_to_p_semis.items(),
        key=lambda x: -get_wins(x[0]) - x[1],
    )
    i_line = 0
    for i_item, item in enumerate(oppo_list + ['P(Semis)', 'Cumulative P.']):
        infographic.text(
            f'{item}',
            (
                x_offset + 0.1 + i_item * col_width,
                i_line * line_height,
            ),
            ha='right',
            font_size=font_size / max(1, len(item) / 8),
        )
    i_line += 1
    for complete_result_id, p_semis in sorted_id_and_p:
        n_wins = get_wins(complete_result_id)
        if n_wins != prev_n_wins:
            infographic.text(
                f'{n_wins} Wins',
                (x_offset, (1 + i_line) * line_height),
                ha='left',
                font_size=font_size,
            )
            i_line += 1
        prev_n_wins = n_wins

        p = complete_result_id_to_n[complete_result_id] / n
        p_cum += p

        p_semis_str = f'{p_semis:.0%}'
        if p_semis > 1 - EPSILON:
            p_semis_str = '100%'
        if p_semis < EPSILON:
            p_semis_str = '0%'

        for i_item, item in enumerate(
            complete_result_id.split(STR_GAP)
            + [
                f'{p_semis_str}',
                f'{p_cum:.0%}',
            ]
        ):
            if i_item == n_oppos + 1:
                color = 'black'
            elif item in [CHAR_WIN, '100%']:
                color = 'green'
            elif item in [CHAR_LOSE, '0%']:
                color = 'red'
            else:
                color = 'orange'
            infographic.text(
                f'{item}',
                (
                    x_offset + 0.1 + i_item * col_width,
                    i_line * line_height,
                ),
                ha='right',
                font_size=font_size,
                color=color,
            )
        i_line += 1

    date_str = timex.format_time(timex.get_unixtime(), '%b %d')
    team_long_name = to_long_name(team_0)
    infographic.header(
        f'Path Ahead for {team_long_name}* · {date_str}',
    )
    infographic.subheader('2021 ICC Men\'s T20 World Cup')

    infographic.supfooter(
        f'* Based on {N_MONTE:,} Monte Carlo Simulations'
        + ' and time-weighted history of match results',
    )
    infographic.footer('Visualization & Analysis by @nuuuwan')

    infographic.save(f'/tmp/cricket_mens_t20_wc_2021.path.{team_0}.png')
