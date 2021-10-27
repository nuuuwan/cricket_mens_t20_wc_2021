import os

from utils import timex, tsv

from cricket_mens_t20_wc_2021._constants import DIR_DATA

AGENDA_FILE = os.path.join(DIR_DATA, 'wc_agenda.tsv')


def load_agenda():
    def clean(d):
        return {
            'match_no': (int)(d['match_no']),
            'team_1': d['team_1'],
            'team_2': d['team_2'],
            'date_id': d['date_id'],
            'winner': (int)(d['winner']) if d.get('winner') else '',
        }

    return list(map(clean, tsv.read(AGENDA_FILE)))


def load_agenda_completed():
    return list(
        filter(
            lambda match: match['winner'] in [0, 1, 2],
            load_agenda(),
        )
    )


def get_last_match_no():
    agenda = load_agenda_completed()
    return max(
        list(
            map(
                lambda match: match['match_no'],
                agenda,
            )
        )
    )


def get_matches_by_days_delta(days_delta):
    date_id = timex.get_date_id(
        timex.get_unixtime() + timex.SECONDS_IN.DAY * days_delta
    )
    return list(
        filter(
            lambda match: match['date_id'] == date_id,
            load_agenda(),
        )
    )


def get_yesterdays_matches():
    return get_matches_by_days_delta(-1)


def get_todays_matches():
    return get_matches_by_days_delta(0)


if __name__ == '__main__':
    print(get_last_match_no())
    print(get_yesterdays_matches())
    print(get_todays_matches())
