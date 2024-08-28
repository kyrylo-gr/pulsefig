from typing import TYPE_CHECKING, Literal, Optional, Union

if TYPE_CHECKING:
    from matplotlib.axes import Axes

_TEXT_SIZE_TYPE = Optional[Union[str, float, int]]


class Annotation:
    x0: float
    x1: float
    y0: float
    y1: float
    text: Optional[str]
    ha: str = "center"
    va: str = "bottom"

    text_size: _TEXT_SIZE_TYPE = None
    group: Optional[str] = None

    def __init__(
        self,
        *,
        x0: Optional[float] = None,
        x1: Optional[float] = None,
        y0: Optional[float] = None,
        y1: Optional[float] = None,
        text: Optional[str] = None,
        va: str = "bottom",
        ha: str = "center",
        text_size: _TEXT_SIZE_TYPE = None,
        arrowstyle: str = "<->",
        color: Optional[str] = None,
    ) -> None:
        if y0 is not None and y1 is None:
            y1 = y0
        if x0 is not None and x1 is None:
            x1 = x0
        if x0 is None or x1 is None:
            raise ValueError("At least one x-coordinate 'x0' must be specified")
        if y0 is None or y1 is None:
            raise ValueError("At least one y-coordinate 'y0' must be specified")

        self.x0 = x0
        self.x1 = x1
        self.y0 = y0
        self.y1 = y1
        self.text = text
        self.va = va
        self.ha = ha

        self.arrowstyle = arrowstyle

        self.text_size = text_size
        self.color = color

    @property
    def orientation(self) -> Literal["vertical", "horizontal", "diagonal", "point"]:
        if self.x0 == self.x1:
            if self.y0 == self.y1:
                return "point"
            return "vertical"
        if self.y0 == self.y1:
            return "horizontal"
        return "diagonal"

    @property
    def start(self):
        if self.orientation == "vertical":
            return min(self.y0, self.y1)
        if self.orientation == "horizontal":
            return min(self.x0, self.x1)
        if self.orientation == "diagonal":
            raise ValueError("Diagonal orientation does not have a start point")

    @property
    def end(self):
        if self.orientation == "vertical":
            return max(self.y0, self.y1)
        if self.orientation == "horizontal":
            return max(self.x0, self.x1)
        if self.orientation == "diagonal":
            raise ValueError("Diagonal orientation does not have an end point")

    def draw(self, ax: "Axes", text_kwargs: Optional[dict] = None, **kwargs):
        kwargs.setdefault("arrowprops", {"arrowstyle": self.arrowstyle})
        if self.color:
            kwargs.setdefault("color", self.color)

        if self.orientation != "point":
            ax.annotate(
                "",
                xy=(self.x0, self.y0),
                xycoords="data",
                xytext=(self.x1, self.y1),
                textcoords="data",
                **kwargs,
            )
        if self.text:
            text_kwargs = text_kwargs or {}
            if self.text_size:
                text_kwargs["size"] = self.text_size

            ax.annotate(
                self.text,
                ((float(self.x0 + self.x1)) / 2, (float(self.y0 + self.y1)) / 2),
                ha=self.ha,
                va=self.va,
                **text_kwargs,
            )
        return self

    @classmethod
    def horizontal(
        cls,
        start: Union[float, int],
        end: Union[float, int],
        y: Union[float, int],
        text: Optional[str] = None,
        *,
        ha="center",
        va="bottom",
        text_size: _TEXT_SIZE_TYPE = None,
    ):
        return cls(
            x0=start, x1=end, y0=y, y1=y, text=text, ha=ha, va=va, text_size=text_size
        )

    @classmethod
    def vertical(
        cls,
        start: Union[float, int],
        end: Union[float, int],
        x: Union[float, int],
        text=None,
        *,
        ha="left",
        va="center",
        text_size: _TEXT_SIZE_TYPE = None,
    ):
        return cls(
            x0=x, x1=x, y0=start, y1=end, text=text, ha=ha, va=va, text_size=text_size
        )

    @classmethod
    def point(
        cls,
        x: Union[float, int],
        y: Union[float, int],
        text=None,
        *,
        ha="center",
        va="center",
        text_size: _TEXT_SIZE_TYPE = None,
    ):
        return cls(x0=x, x1=x, y0=y, y1=y, text=text, ha=ha, va=va, text_size=text_size)

    @classmethod
    def line(cls, x0: float, y0: float, x1: float, y1: float, **kwargs):
        return cls(x0=x0, x1=x1, y0=y0, y1=y1, arrowstyle="-", **kwargs)
