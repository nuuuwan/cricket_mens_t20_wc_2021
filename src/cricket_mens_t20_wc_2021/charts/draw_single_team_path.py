from utils import timex

CHAR_WIN = '🟢'
CHAR_NOT_SURE = '🟠'
CHAR_LOSE = '🔴'

def get_wins(complete_result_id):
    return complete_result_id.count(CHAR_WIN)

def draw_single_team_path(team_0, outcomes_list, semi_finals_teams_list):
    n = len(outcomes_list)
    complete_result_id_to_n = {}
    complete_result_id_to_n_semis = {}
    date_id_today = timex.get_date_id()
    for outcomes, semi_finals_teams in zip(outcomes_list, semi_finals_teams_list):
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
                    result_str = CHAR_WIN + team_2
                elif winner == 2:
                    result_str = CHAR_LOSE + team_2
            elif team_0 == team_2:
                if winner == 1:
                    result_str = CHAR_LOSE + team_1
                elif winner == 2:
                    result_str = CHAR_WIN + team_1

            if result_str:
                result_str_list.append(result_str)

        complete_result_id = ' '.join(result_str_list)
        is_qualified = (team_0 in semi_finals_teams)

        if complete_result_id not in complete_result_id_to_n:
            complete_result_id_to_n[complete_result_id] = 0
            complete_result_id_to_n_semis[complete_result_id] = 0

        complete_result_id_to_n[complete_result_id] += 1
        if is_qualified:
            complete_result_id_to_n_semis[complete_result_id] += 1

    complete_result_id_to_p_semis = dict(
        list(map(
            lambda x: [x[0] , x[1]  / complete_result_id_to_n[x[0]]],
            complete_result_id_to_n_semis.items(),
        ))
    )
    p_cum = 0
    EPSILON = 0.00001
    prev_n_wins = None
    for complete_result_id, p_semis in sorted(
        complete_result_id_to_p_semis.items(),
        key=lambda x: -get_wins(x[0]) - x[1],
    ):
        n_wins = get_wins(complete_result_id)
        if n_wins != prev_n_wins:
            print(f'\n{n_wins} Wins')
        p = complete_result_id_to_n[complete_result_id] / n
        p_cum += p

        if p_semis < EPSILON:
            p_semis_str = CHAR_LOSE
        elif p_semis > 1 - EPSILON:
            p_semis_str = CHAR_WIN
        else:
            p_semis_str = CHAR_NOT_SURE

        p_semis_str += f'{p_semis:.0%}'
        print(f'\t{complete_result_id} {p_semis_str} {p_cum:.0%}')
        prev_n_wins = n_wins
