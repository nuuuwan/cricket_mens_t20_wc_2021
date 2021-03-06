from utils import timex

from cricket_mens_t20_wc_2021._constants import N_MONTE, TEAM_TO_COLOR
from cricket_mens_t20_wc_2021._infographicx import (FONT_SIZE_NORMAL,
                                                    Infographic)


def draw_chart_p_winning(split_to_sorted_team_semi_p, title, file_id):
    n_rows = len(split_to_sorted_team_semi_p.keys())
    infographic = Infographic(n_rows=n_rows)
    infographic.hide_box()

    for i_split, (split, sorted_team_x_p) in enumerate(
        split_to_sorted_team_semi_p.items()
    ):
        labels = []
        sizes = []
        colors = []

        for team, p in sorted_team_x_p:
            labels.append(team)
            sizes.append(p)
            colors.append(TEAM_TO_COLOR[team])
        max_size = max(sizes)
        ax = infographic.get_ax(i_split, 0)

        ax.set_title(
            split, fontsize=FONT_SIZE_NORMAL, loc='right', y=0.5, ha='right'
        )
        bars = ax.bar(x=labels, height=sizes, color=colors)
        labels = list(
            map(
                lambda size: f'{size:.1%}',
                sizes,
            )
        )

        ax.bar_label(bars, labels=labels, fontsize=FONT_SIZE_NORMAL)
        ax.tick_params(axis='x', labelsize=FONT_SIZE_NORMAL)
        ax.set_ylim([0, max_size * 1.15])

    date_str = timex.format_time(timex.get_unixtime(), '%b %d')
    infographic.header(f'P({title})* · {date_str}')
    infographic.subheader('2021 ICC Men\'s T20 World Cup')

    if 'oddschecker' in file_id:
        supfooter_text = '* Data from www.oddschecker.com'
    else:
        supfooter_text = (
            f'* Based on {N_MONTE:,} Monte Carlo Simulations'
            + ' and time-weighted history of match results'
        )
    infographic.supfooter([supfooter_text])
    infographic.footer('Visualization & Analysis by @nuuuwan')

    infographic.save(f'/tmp/cricket_mens_t20_wc_2021.{file_id}.png')
