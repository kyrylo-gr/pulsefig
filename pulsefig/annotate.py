from typing import TYPE_CHECKING, Any, Callable, Dict, Literal, Optional, Union

from .styles import get_final_style
from .utils import filter_none, remove_prefix_from_dict

if TYPE_CHECKING:
    from matplotlib.axes import Axes

_TEXT_SIZE_TYPE = Optional[Union[str, float, int]]
_TEXT_TYPE = Optional[Union[str, Callable]]


class Annotation:
    x0: float
    x1: float
    y0: float
    y1: float
    text: _TEXT_TYPE
    text_style: Dict[str, Any]
    annotation_style: Dict[str, Any]

    form: Literal["straight", "curve"]

    text_size: _TEXT_SIZE_TYPE = None
    group: Optional[str] = None

    def __init__(
        self,
        *,
        x0: Optional[float] = None,
        x1: Optional[float] = None,
        y0: Optional[float] = None,
        y1: Optional[float] = None,
        text: _TEXT_TYPE = None,
        va: str = "bottom",
        ha: str = "center",
        text_size: _TEXT_SIZE_TYPE = None,
        arrowstyle: str = "<->",
        color: Optional[str] = None,
        text_color: Optional[str] = None,
        form: Literal["straight", "curve"] = "straight",
        **text_style,
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

        self.text_size = text_size
        self.form = form

        self.text_style = filter_none(text_style)
        self.text_style.update(
            filter_none(
                {
                    "text.va": va,
                    "text.ha": ha,
                    "text.fontsize": text_size,
                    "text.color": text_color or color,
                }
            )
        )

        self.annotation_style = filter_none(
            {
                "annotation.color": color,
                "annotation.arrowprops": {
                    "arrowstyle": arrowstyle,
                    "shrinkA": 0,
                    "shrinkB": 0,
                },
            }
        )

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

    def draw(
        self,
        ax: "Axes",
        style: Optional[dict] = None,
        annotation_style: Optional[dict] = None,
    ):
        text_style = get_final_style(style, self.text_style)
        annotation_style = get_final_style(style, self.annotation_style)

        if self.orientation != "point":
            ax.annotate(
                "",
                xy=(self.x0, self.y0),
                xycoords="data",
                xytext=(self.x1, self.y1),
                textcoords="data",
                **remove_prefix_from_dict(annotation_style, "annotation."),
            )
        if self.text:
            if isinstance(self.text, str):
                ax.text(
                    (float(self.x0 + self.x1)) / 2,
                    (float(self.y0 + self.y1)) / 2,
                    self.text,
                    **remove_prefix_from_dict(text_style, "text."),
                )
            else:
                self.text(
                    ax=ax,
                    x0=(float(self.x0 + self.x1)) / 2,
                    y0=(float(self.y0 + self.y1)) / 2,
                    **remove_prefix_from_dict(text_style, "text."),
                )

        return self

    @classmethod
    def horizontal(
        cls,
        start: Union[float, int],
        end: Union[float, int],
        y: Union[float, int],
        text: _TEXT_TYPE = None,
        *,
        ha="center",
        va="bottom",
        text_size: _TEXT_SIZE_TYPE = None,
        **kwargs,
    ):
        return cls(
            x0=start,
            x1=end,
            y0=y,
            y1=y,
            text=text,
            ha=ha,
            va=va,
            text_size=text_size,
            **kwargs,
        )

    @classmethod
    def vertical(
        cls,
        start: Union[float, int],
        end: Union[float, int],
        x: Union[float, int],
        text: _TEXT_TYPE = None,
        *,
        ha="left",
        va="center",
        text_size: _TEXT_SIZE_TYPE = None,
        **kwargs,
    ):
        return cls(
            x0=x,
            x1=x,
            y0=start,
            y1=end,
            text=text,
            ha=ha,
            va=va,
            text_size=text_size,
            **kwargs,
        )

    @classmethod
    def point(
        cls,
        x: Union[float, int],
        y: Union[float, int],
        text: _TEXT_TYPE = None,
        *,
        ha="center",
        va="center",
        text_size: _TEXT_SIZE_TYPE = None,
        **kwargs,
    ):
        return cls(
            x0=x,
            x1=x,
            y0=y,
            y1=y,
            text=text,
            ha=ha,
            va=va,
            text_size=text_size,
            **kwargs,
        )

    @classmethod
    def line(cls, x0: float, y0: float, x1: float, y1: float, **kwargs):
        return cls(x0=x0, x1=x1, y0=y0, y1=y1, arrowstyle="-", **kwargs)
