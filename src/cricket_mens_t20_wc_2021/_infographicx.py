import matplotlib.pyplot as plt

DPI_IMAGE_RESOLUTION = 600
FIG_WIDTH, FIG_HEIGHT = 8, 4.5

X_MID = 0.5
PADDING = 0.15
FONT_SIZE_NORMAL = 8 * (PADDING / 0.15)
FONT_SIZE_HEADER = FONT_SIZE_NORMAL * 1.5
FONT_SIZE_SUBHEADER = FONT_SIZE_NORMAL

Y_HEADER = 0.8 * PADDING / 3
Y_SUBHEADER = 0.8 * 2 * PADDING / 3
Y_SUBHEADER_GAP = PADDING / 5

PADDING_TIGHT_LAYOUT = 2
DEFAULT_FONT_FAMILY = 'Futura'
plt.rcParams['font.family'] = DEFAULT_FONT_FAMILY


def get_inner(xy):
    return list(
        map(
            lambda z: z * (1 - PADDING * 2) + PADDING,
            xy,
        )
    )


def get_vflip(xy):
    x, y = xy
    return x, 1 - y


class Infographic:
    def __init__(self, n_rows=1, n_cols=1):
        self.__fig__ = plt.gcf()
        self.__n_rows__ = n_rows
        self.__n_cols__ = n_cols

        self.__fig__, self.__axes__ = plt.subplots(nrows=n_rows, ncols=n_cols)
        plt.subplots_adjust(bottom=PADDING, top=1 - PADDING)

        self.__fig__.set_size_inches(FIG_WIDTH, FIG_HEIGHT)
        self.__patches__ = []

    def save(self, image_file):
        self.__fig__.patches.extend(self.__patches__)
        self.__fig__.tight_layout(pad=PADDING_TIGHT_LAYOUT)
        self.__fig__.savefig(image_file, dpi=DPI_IMAGE_RESOLUTION)
        plt.close()

    def hide_axis(self):
        plt.axis('off')

    def hide_box(self):
        for ax in self.get_ax_list():
            ax.get_yaxis().set_visible(False)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)

    def get_ax_list(self):
        if self.__n_rows__ == 1 and self.__n_cols__ == 1:
            return [self.__axes__]
        return self.__axes__

    def get_ax(self, i_row, i_col=0):
        if self.__n_rows__ == 1 and self.__n_cols__ == 1:
            return self.__axes__
        if self.__n_cols__ == 1:
            return self.__axes__[i_row]
        return self.__axes__[i_row, i_col]

    def text_inner(
        self,
        text,
        xy,
        font_size=FONT_SIZE_NORMAL,
        ha='center',
        color='black',
        font_weight='normal',
    ):
        plt.annotate(
            text,
            get_vflip(xy),
            xycoords='figure fraction',
            fontsize=font_size,
            ha=ha,
            va='center',
            color=color,
            fontweight=font_weight,
        )

    def text(
        self,
        text,
        xy,
        font_size=FONT_SIZE_NORMAL,
        ha='center',
        color='black',
        font_weight='normal',
    ):
        xy_inner = get_inner(xy)
        self.text_inner(text, xy_inner, font_size, ha, color, font_weight)

    def header(self, text):
        self.text_inner(
            text,
            (X_MID, Y_HEADER),
            font_size=FONT_SIZE_HEADER,
        )

    def subheader(self, text):
        self.text_inner(
            text,
            (X_MID, Y_SUBHEADER),
            font_size=FONT_SIZE_SUBHEADER,
        )

    def supfooter(self, text_list):
        n_text_list = len(text_list)
        for i, text in enumerate(text_list):
            self.text_inner(
                text,
                (
                    X_MID,
                    1 - Y_SUBHEADER + (i + 1 - n_text_list) * Y_SUBHEADER_GAP,
                ),
                font_size=FONT_SIZE_SUBHEADER,
            )

    def footer(self, text):
        self.text_inner(
            text,
            (X_MID, 1 - Y_HEADER),
            font_size=FONT_SIZE_HEADER,
        )

    def circle(self, xy, radius, color='red'):
        x, y = xy
        xy2 = get_vflip(get_inner([x - radius, y - radius * 0.25]))
        self.__patches__.append(
            plt.Circle(
                xy2,
                radius,
                color=color,
                figure=self.__fig__,
                transform=self.__fig__.transFigure,
            )
        )
