import os
import matplotlib.pyplot as plt
from utils import timex

from cricket_mens_t20_wc_2021._constants import N_MONTE, TEAM_TO_COLOR, DPI_IMAGE_RESOLUTION

 
def draw_chart_p_winning(split_to_sorted_team_semi_p, title, file_id):
    n_rows = len(split_to_sorted_team_semi_p.keys())
    n_cols = 1
    fig, axes = plt.subplots(nrows=n_rows, ncols=n_cols)

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
        sizes_p = list(map(lambda size: size * 100, sizes))
        if n_rows > 1:
            ax = axes[i_split]
        else:
            ax = axes
        alpha = 0.2 if 'Pre-Match' in split else 1.0
        bars = ax.bar(x=labels, height=sizes_p, color=colors, alpha=alpha)

        ax.bar_label(bars, fmt='%4.2g%%', fontsize=8, alpha=alpha)
        ax.get_yaxis().set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        plt.subplots_adjust(bottom=0.2, top=0.8)
        ax.set_title(
            split, fontsize=6, loc='right', y=0.5, ha='right', alpha=alpha
        )

    fig.set_size_inches(8, 4.5)
    fig.tight_layout(pad=2.9)

    if 'oddschecker' in file_id:
        plt.figtext(
            0.5,
            0.05,
            '* Data from www.oddschecker.com',
            ha='center',
            fontsize=6,
        )
    else:
        plt.figtext(
            0.5,
            0.05,
            f'* Based on {N_MONTE:,} Monte Carlo Simulations'
            + ' and time-weighted history of match results',
            ha='center',
            fontsize=6,
        )

    plt.figtext(
        0.5,
        0.02,
        'Visualization & Analysis by @nuuuwan',
        fontsize=8,
        ha='center',
    )

    date_str = timex.format_time(timex.get_unixtime(), '%b %d')
    plt.suptitle(
        '2021 ICC Men\'s T20 World Cup' + f' · P({title})* · {date_str}',
    )

    image_file = f'/tmp/cricket_mens_t20_wc_2021.{file_id}.png'
    fig.savefig(image_file, dpi=DPI_IMAGE_RESOLUTION)
    os.system(f'open -a firefox {image_file}')

    plt.close()
