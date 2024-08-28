from copy import deepcopy
from typing import TYPE_CHECKING, Callable, List, Optional, TypeVar, Union

import matplotlib

from .element import Element, PlotStyle
from .styles import DEFAULT_COLOR
from .utils import get_start_end_time

if TYPE_CHECKING:
    from matplotlib.axes import Axes
_LE = TypeVar("_LE", bound="LineEnsemble")
_L = TypeVar("_L", bound="Line")

DEFAULT_ASPECT_RATIO = lambda x: ((x * 1) / 6)  # noqa: E731


class Line:
    name: str
    elements: List[Element]
    line_color: Optional[str] = None
    style: Optional[PlotStyle] = None
    y_offset: float = 0.0
    y_index: int = 0
    text_offset: float = 1.0

    _time_start: Optional[float] = None
    _time_end: Optional[float] = None

    def __init__(
        self,
        name: str,
        elements: Optional[List[Element]] = None,
        style: Optional[PlotStyle] = None,
    ) -> None:
        self.name = name
        self.elements = [] if elements is None else elements
        self.style = style

    def attach_elements(self: _L, *element: Element) -> _L:
        self.elements.extend(element)
        self.predraw()
        return self

    def set(self: _L, **kwargs) -> _L:
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self

    def predraw(self: _L, y_offset: Optional[float] = None) -> _L:
        if y_offset is not None:
            self.y_offset = y_offset
        last_end = 0
        for elm in self.elements:
            elm.predraw(possible_start=last_end, y_offset=y_offset)
            last_end = elm.end if elm.end is not None else last_end

        self._time_start, self._time_end = get_start_end_time(self)

        return self

    def draw(
        self: _L,
        ax: "Axes",
        *,
        style: Optional[PlotStyle] = None,
        y_offset: Optional[float] = None,
        y_index: int = 0,
        time_start: Optional[float] = None,
        time_end: Optional[float] = None,
    ) -> _L:
        full_style = self.style or {}
        full_style.update(style or {})

        if y_offset is not None:
            self.y_offset = y_offset
        self.y_index = y_index

        if time_start is None or time_end is None:
            self.predraw(y_offset=self.y_offset)
            if self._time_start is None or self._time_end is None:
                raise ValueError(
                    "Start or end time is None. Provide it or call predraw"
                )
            time_start = self._time_start
            time_end = self._time_end

        line_color = self.line_color or full_style.get(
            "color", DEFAULT_COLOR  # colors[y_index % len(colors)]
        )
        ax.plot(
            [time_start - self.text_offset, time_end],
            [self.y_offset] * 2,
            color=line_color,
        )
        ax.annotate(
            self.name,
            (time_start - self.text_offset, self.y_offset),
            ha="left",
            va="bottom",
            size=matplotlib.rcParams["figure.labelsize"],
        )
        for elm in self.elements:
            elm.draw(
                ax,
                style=self.style,
                y_index=y_index,
            )

        return self

    def __add__(self: _L, other: Union[_L, "LineEnsemble"]) -> "LineEnsemble":
        if isinstance(other, Line):
            return LineEnsemble(lines=[self, other])
        elif isinstance(other, LineEnsemble):
            other.lines.insert(0, self)
        return other
        # return LineEnsemble(lines=[self, other])

    def copy(self) -> "Line":
        return deepcopy(self)

    def __str__(self) -> str:
        return f"{self.__class__.__name__} : {self.name}"

    def __repr__(self) -> str:
        if self.elements:
            elements = "\n\t" + "\n\t".join([str(elm) for elm in self.elements])
        else:
            elements = ""

        return (
            f"{self.__class__.__name__} {self.y_index} : {self.name} "
            f"with {len(self.elements)} elements {elements}"
        )


class LineEnsemble:
    lines: List[Line]
    style: Optional[PlotStyle] = None
    _time_start: Optional[float] = None
    _time_end: Optional[float] = None

    def __init__(self, *, lines: List[Line], style: Optional[PlotStyle] = None):
        self.lines = lines
        self.style = style

    def attach_lines(self: _LE, *line: Line) -> _LE:
        self.lines.extend(line)
        return self

    def __add__(self: _LE, other: Union["LineEnsemble", "Line"]) -> _LE:
        if isinstance(other, Line):
            self.lines.append(other)
        else:
            self.lines.extend(other.lines)
        return self

    def __raddd__(self: _LE, other: Union["LineEnsemble", "Line"]) -> _LE:
        if isinstance(other, Line):
            self.lines.insert(0, other)
        else:
            self.lines.extend(other.lines)
        return self

    def predraw(self: _LE) -> _LE:
        for i, line in enumerate(self.lines):
            y_offset = (len(self.lines) - i - 1) * 1.5
            line.predraw(y_offset=y_offset)
        self._time_start, self._time_end = get_start_end_time(self)
        return self

    def draw(
        self: _LE,
        ax: "Axes",
        *,
        style: Optional[PlotStyle] = None,
        time_start: Optional[float] = None,
        time_end: Optional[float] = None,
    ) -> _LE:
        style = (self.style or {}).update(style or {})
        if time_start is None or time_end is None:
            if self._time_start is None or self._time_end is None:
                self.predraw()
                if self._time_start is None or self._time_end is None:
                    raise ValueError(
                        "Start or end time is None and cannot be calculated"
                    )
            time_start, time_end = self._time_start, self._time_end

        time_duration = time_end - time_start
        time_start -= time_duration * 0.05
        time_end += time_duration * 0.05

        for i, line in enumerate(self.lines):
            # y_offset = (len(self.lines) - i - 1) * 1.5
            line.draw(
                ax,
                style=style,
                y_index=i,
                time_start=time_start,
                time_end=time_end,
            )
        return self

    def config_ax(
        self: _LE,
        ax: "Axes",
        *,
        aspect: Optional[Union[float, Callable[[int], float]]] = DEFAULT_ASPECT_RATIO,
        axis_off: bool = True,
    ) -> _LE:
        if axis_off:
            ax.axis("off")
        if aspect is not None:
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            xs = xlim[1] - xlim[0]
            ys = ylim[1] - ylim[0]

            if callable(aspect):
                # print(f"set aspect to {aspect(len(self.lines))}")
                ax.set_aspect(aspect(len(self.lines)) / (ys / xs))
            else:
                ax.set_aspect(aspect / (ys / xs))
        return self

    def copy(self) -> "LineEnsemble":
        return deepcopy(self)

    def __str__(self) -> str:
        return f"{self.__class__.__name__} with {len(self.lines)} lines"

    def __repr__(self) -> str:
        if self.lines:
            lines = ":\n\t" + "\n\t".join([str(line) for line in self.lines])
        else:
            lines = ""
        return f"{self.__class__.__name__} with {len(self.lines)} lines {lines}"
