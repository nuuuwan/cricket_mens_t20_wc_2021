import matplotlib.pyplot as plt

DPI_IMAGE_RESOLUTION = 600
FIG_WIDTH, FIG_HEIGHT = 8, 4.5

X_MID = 0.5
Y_HEADER = 0.04
FONT_SIZE_HEADER = 12
Y_SUBHEADER = 0.09
FONT_SIZE_SUBHEADER = 8
PADDING = 0.15


class Infographic:
    def __init__(self):
        self.__fig__ = plt.gcf()
        self.__fig__.set_size_inches(FIG_WIDTH, FIG_HEIGHT)

    def save(self, image_file):
        plt.axis('off')
        self.__fig__.savefig(image_file, dpi=DPI_IMAGE_RESOLUTION)
        plt.close()

    def text_inner(self, text, xy, font_size=8, ha='center', color='black'):
        x, y = xy
        y_rev = 1 - y
        plt.annotate(
            text,
            (x, y_rev),
            xycoords='figure fraction',
            fontsize=font_size,
            ha=ha,
            va='center',
            color=color,
        )

    def text(self, text, xy, font_size=8, ha='center', color='black'):
        x_inner, y_inner = list(
            map(
                lambda z: z * (1 - PADDING * 2) + PADDING,
                xy,
            )
        )
        self.text_inner(text, (x_inner, y_inner), font_size, ha, color)

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
