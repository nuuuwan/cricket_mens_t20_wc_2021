import os

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from utils import timex

from cricket_mens_t20_wc_2021._constants import TEAM_TO_COLOR, WHITE_FORE_TEAMS

N_MONTE = 100_000

DPI_IMAGE_RESOLUTION = 600


def draw_chart_p_winning(sorted_team_winner_p, title):
    labels = []
    sizes = []
    colors = []
    others_size = 0

    if title == 'Winning':
        OTHER_LIMIT = 0.05
    else:
        OTHER_LIMIT = 0.0

    for label, sorted_team_x_p in [
        ['P(Winning)', sorted_team_winner_p],
    ]:
        print('-' * 32)
        print(label)
        print('-' * 32)
        for team, p in sorted_team_x_p:
            if p > OTHER_LIMIT:
                labels.append(team)
                sizes.append(p)
                colors.append(TEAM_TO_COLOR[team])
            else:
                others_size += p

        if others_size > 0:
            labels.append('Others')
            sizes.append(others_size)
            colors.append('gray')
        print('...')

    fig = plt.gcf()
    fig.set_size_inches(8, 4.5)

    plt.annotate(
        'ICC Men\'s T20 World Cup - 2021',
        (0.5, 0.97),
        xycoords='figure fraction',
        ha='center',
        fontsize=9,
    )
    date_str = timex.format_time(timex.get_unixtime(), '%B %d, %Y')
    plt.annotate(
        f'Probability of {title} (as of {date_str})*',
        (0.5, 0.91),
        xycoords='figure fraction',
        ha='center',
        fontsize=15,
    )
    if sum(sizes) > 1.1:
        plt.margins(y=0.2)

        sizes_p = list(map(lambda size: size * 100, sizes))

        bars = plt.gca().bar(x=labels, height=sizes_p, color=colors)
        plt.gca().bar_label(bars, fmt='%.0f%%')

        plt.annotate(
            f'* Based on {N_MONTE:,} Monte Carlo Simulations'
            + ' and time-weighted history of match results',
            (0.87, 0.8),
            xycoords='figure fraction',
            ha='right',
            fontsize=6,
        )

        plt.annotate(
            'Visualization & Analysis by @nuuuwan',
            (0.87, 0.75),
            xycoords='figure fraction',
            ha='right',
            fontsize=9,
        )

        plt.gca().yaxis.set_major_formatter(
            FuncFormatter(lambda y, _: '{:.0f}%%'.format(y))
        )

    else:
        _, texts, auto_texts = plt.pie(
            sizes,
            labels=labels,
            colors=colors,
            autopct='%1.0f%%',
            startangle=90,
            normalize=True,
        )
        for i, text in enumerate(texts):
            if text.get_text() in WHITE_FORE_TEAMS:
                auto_texts[i].set_color('white')
            size = sizes[i]
            font_size = max(6, min(24, 36 * size))
            auto_texts[i].set_fontsize(font_size)
            texts[i].set_fontsize(font_size)

        plt.annotate(
            f'* Based on {N_MONTE:,} Monte Carlo Simulations'
            + ' and time-weighted history of match results',
            (0.5, 0.09),
            xycoords='figure fraction',
            ha='center',
            fontsize=6,
        )

        plt.annotate(
            'Visualization & Analysis by @nuuuwan',
            (0.5, 0.04),
            xycoords='figure fraction',
            ha='center',
            fontsize=9,
        )

    title_str = title.replace(' ', '').lower()
    image_file = f'/tmp/cricket_mens_t20_wc_2021.{title_str}.png'
    fig.savefig(image_file, dpi=DPI_IMAGE_RESOLUTION)
    os.system(f'open -a firefox {image_file}')

    plt.close()
