import matplotlib.pyplot as plt

DPI_IMAGE_RESOLUTION = 600
FIG_WIDTH, FIG_HEIGHT = 8, 4.5

X_MID = 0.5
Y_HEADER = 0.04
FONT_SIZE_HEADER = 12
Y_SUBHEADER = 0.09
FONT_SIZE_SUBHEADER = 8
PADDING = 0.15


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
    def __init__(self):
        self.__fig__ = plt.gcf()
        self.__fig__.set_size_inches(FIG_WIDTH, FIG_HEIGHT)
        self.__patches__ = []

    def save(self, image_file):
        self.__fig__.patches.extend(self.__patches__)
        plt.axis('off')
        self.__fig__.savefig(image_file, dpi=DPI_IMAGE_RESOLUTION)
        plt.close()

    def text_inner(
        self,
        text,
        xy,
        font_size=8,
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
        font_size=8,
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

    def supfooter(self, text):
        self.text_inner(
            text,
            (X_MID, 1 - Y_SUBHEADER),
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
