import os

from utils import tsv

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


if __name__ == '__main__':
    print(load_agenda()[-1])
