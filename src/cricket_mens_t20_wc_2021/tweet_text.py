import os

from utils import filex, timex

from cricket_mens_t20_wc_2021._utils import to_hashtag
from cricket_mens_t20_wc_2021.wc_agenda import (get_last_match_no,
                                                get_todays_matches,
                                                get_yesterdays_matches)

TWEET_TEXT_FILE = '/tmp/cricket_mens_t20_wc_2021.tweet.txt'


def format_match(match):
    team_1_str = to_hashtag(match['team_1'])
    team_2_str = to_hashtag(match['team_2'])
    winner = match['winner']

    if winner == 1:
        return f'{team_1_str} beat {team_2_str}'
    if winner == 2:
        return f'{team_2_str} beat {team_1_str}'
    if winner == 0:
        return 'No Result'
    return f'{team_2_str} vs. {team_1_str}'


def store_tweet_text():
    match_no = get_last_match_no()
    date_str = timex.format_time(timex.get_unixtime(), '%b %d')
    yesterdays_matches = get_yesterdays_matches()
    todays_matches = get_todays_matches()
    n_todays_matches = len(todays_matches)

    blurb_yesterday = '\n'.join(
        list(map(format_match, yesterdays_matches)),
    )

    blurb_today = '\n'.join(
        list(map(format_match, todays_matches)),
    )

    _break = '-' * 32

    tweet_text = f'''

{_break}

#T20WorldCup PREDICTIONS - {date_str} (after match {match_no})

1/ P(Reaching the Semis)

{blurb_yesterday}

@T20WorldCup #Cricket

{_break}

2/ P(Winning) #T20WorldCup

@T20WorldCup #Cricket

{_break}

3/ Today's #T20WorldCup Matches

{n_todays_matches} matches today.

{blurb_today}

@T20WorldCup #Cricket

{_break}

4/ Most Likely #T20WorldCup Outcomes

@T20WorldCup #Cricket

{_break}

5/ @OddsChecker - #T20WorldCup Betting Odds

I'm no betting man, but here's what the betting markets say about P(Winning).

@T20WorldCup #Cricket

{_break}

6/ CAVEATS & CODE

⚠️ The data used for these #T20WorldCup predictions are sparse and noisy.
Hence, some predictions are likely to change.

You can find the code at
https://github.com/nuuuwan/cricket_mens_t20_wc_2021.

Feel free to fork/comment/report issues.

@T20WorldCup @GitHub @ThePSF #Cricket

{_break}

    '''

    filex.write(TWEET_TEXT_FILE, tweet_text)
    os.system(f'open -a atom {TWEET_TEXT_FILE}')


if __name__ == '__main__':
    store_tweet_text()
