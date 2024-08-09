from copy import deepcopy
from typing import (
    TYPE_CHECKING,
    Callable,
    List,
    Optional,
    Tuple,
    TypedDict,
    TypeVar,
    Union,
)

import matplotlib
import numpy as np

from .annotate import Annotation
from .styles import colors

if TYPE_CHECKING:
    from matplotlib.axes import Axes

_Elm = TypeVar("_Elm", bound="Element")
_Data = TypeVar("_Data", bound="Data")


class PlotStyle(TypedDict, total=False):
    color: str
    linestyle: str
    linewidth: float
    marker: str
    markersize: float
    markerfacecolor: str
    markeredgewidth: float
    markeredgecolor: str
    alpha: float
    zorder: int


class Data:
    height: int = 1
    height_points: np.ndarray
    x: np.ndarray
    _length: int = 100
    style: Optional[PlotStyle] = None

    def __init__(self, height: int = 1, x: Optional[np.ndarray] = None):
        self.height = height
        self.height_points = np.ones(self._length)
        self.x = np.linspace(0, 1, self._length) if x is None else x

    def _get_right_x(
        self, x: Optional[np.ndarray], start: float, end: float
    ) -> Tuple[np.ndarray, int, int]:
        if x is None:
            x = self.x
        start_index: int = np.searchsorted(x, start) if start != 0 else 0  # type: ignore
        end_index: int = (
            np.searchsorted(x, end, side="right") if end != 1.0 else len(x)
        )  # type: ignore

        return x[start_index:end_index], start_index, end_index

    def attach_func(
        self: _Data,
        func: Callable[[np.ndarray], np.ndarray],
        x: Optional[np.ndarray] = None,
        start: float = 0,
        end: float = 1.0,
    ) -> _Data:
        x, start_index, end_index = self._get_right_x(x, start, end)
        data = func(x)
        # print(x, data)
        return self.attach_data(
            data, x, start, end, start_index=start_index, end_index=end_index
        )

    def attach_data(
        self: _Data,
        data: np.ndarray,
        x: Optional[np.ndarray] = None,
        start: float = 0,
        end: float = 1,
        *,
        start_index: int = 0,
        end_index: int = -1,
    ) -> _Data:
        x, start_index_, _ = self._get_right_x(x, start, end)

        # print(x, start_index, end_index)

        self.height_points = np.concatenate(
            [
                self.height_points[: start_index + start_index_],
                data,
                self.height_points[end_index + start_index_ :],
            ]
        )
        self.x = np.concatenate(
            [
                self.x[: start_index + start_index_],
                x,
                self.x[end_index + start_index_ :],
            ]
        )

        return self

    def copy(self) -> "Data":
        new_data = Data(self.height, self.x)
        new_data.height_points = self.height_points.copy()
        new_data.style = self.style.copy() if self.style is not None else None
        return new_data

    def set(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self

    def update_style(self: _Data, **kwargs) -> _Data:
        if self.style is None:
            self.style = {}
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        self.style.update(kwargs)  # type: ignore
        return self

    def draw(
        self: _Data,
        ax: "Axes",
        start: float,
        end: float,
        offset_y: float,
        style: Optional[PlotStyle] = None,
    ) -> _Data:
        if style is None:
            style = {}
        if self.style is not None:
            style.update(self.style)

        ax.fill_between(
            self.x * (end - start) + start,
            self.height_points * self.height + offset_y,  # type: ignore
            offset_y,
            **style,
        )

        return self


class Element:
    start: Optional[float]
    end: Optional[float]
    duration: Optional[float]
    delay: float = 0
    height: float = 1

    title: str = ""
    subtitle: str = ""
    xlabel: str = ""
    ylabel: str = ""

    y_offset: float = 0
    style: Optional[PlotStyle] = None
    y_index: int = 0

    annotations: List[Annotation]
    _length: int = 100

    def __init__(
        self,
        start: Optional[Union[float, "Element"]] = None,
        end: Optional[float] = None,
        *,
        duration: Optional[float] = None,
        delay: float = 0,
        height: float = 1,
        name: Optional[str] = None,
    ):
        # if start is None:
        #     raise NotImplementedError("Start time must be specified")
        if isinstance(start, Element):
            start = start.end

        self.start = start
        self.delay = delay

        if end is None:
            if duration is None:
                raise ValueError("End time or duration must be specified")
            self.duration = duration
            end = self.start + duration if self.start is not None else None
        self.end = end

        self.height = height
        self.dataset = [Data()]
        self.name = name
        self.annotations = []

    def set(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self

    def _check_data_index(self, data_index: Optional[int]) -> int:
        if len(self.dataset) > 2 and data_index is None:
            raise ValueError("Data index must be specified for multi-data elements")
        if data_index is None:
            data_index = 0
        return data_index

    def copy_data(self: _Elm, index: int = -1) -> _Elm:
        self.attach_data(self.dataset[index].copy())
        return self

    def update_style(
        self: _Elm,
        data_index: Optional[int] = None,
        **kwargs,
    ) -> _Elm:
        if data_index is None:
            if self.style is None:
                self.style = {}
            kwargs = {k: v for k, v in kwargs.items() if v is not None}
            self.style.update(kwargs)  # type: ignore
            return self
        self.dataset[data_index].update_style(**kwargs)
        return self

    def _get_style(self, style: Optional[PlotStyle] = None) -> PlotStyle:
        if style is None:
            style = {}
        if self.style is not None:
            style.update(self.style)
        if "color" not in style:
            style["color"] = colors[self.y_index % len(colors)]
        return style

    def attach_func(
        self: _Elm,
        func: Callable[[np.ndarray], np.ndarray],
        x: Optional[np.ndarray] = None,
        start: float = 0,
        end: float = 1.0,
        data_index: Optional[int] = None,
    ) -> _Elm:
        if len(self.dataset) > 2 and data_index is None:
            raise ValueError("Data index must be specified for multi-data elements")
        if data_index is None:
            data_index = 0
        self.dataset[data_index].attach_func(func, x, start, end)
        return self

    def attach_data(
        self: _Elm,
        data: np.ndarray | Data,
        x: Optional[np.ndarray] = None,
        start: float = 0,
        end: float = 1,
        data_index: Optional[int] = None,
    ) -> _Elm:
        if isinstance(data, Data):
            self.dataset.append(data)
            return self
        data_index = self._check_data_index(data_index)
        self.dataset[data_index].attach_data(data, x, start, end)
        return self

    def attach_annotation(self: _Elm, annotation: Optional[Annotation]) -> _Elm:
        if annotation is None:
            return self

        self.annotations.append(annotation)
        return self

    def predraw(self: _Elm, possible_start: Optional[float] = None) -> _Elm:
        if self.start is None:
            if possible_start is None:
                raise ValueError("Start time must be specified")
            self.start = possible_start + self.delay

        if self.end is None:
            if self.duration is None:
                raise ValueError("End time or duration must be specified")
            self.end = self.start + self.duration

        return self

    def draw(
        self: _Elm,
        ax: "Axes",
        *,
        style: Optional[PlotStyle] = None,
        y_offset: float = 0.0,
        y_index: int = 0,
    ) -> _Elm:
        if self.start is None or self.end is None:
            raise ValueError(
                "Start or end time is None. Cannot draw element. Call predraw() first"
            )

        self.y_offset = y_offset
        self.y_index = y_index

        style = self._get_style(style)

        for data in self.dataset:
            data.draw(ax, self.start, self.end, y_offset, style)

        # subtitle: str = ""
        # x_label: str = ""
        # y_label: str = ""
        if self.title:
            Annotation.point(
                (self.start + self.end) / 2,
                y_offset + self.height / 2,
                self.title,
                text_size=matplotlib.rcParams["legend.fontsize"],
            ).draw(ax)

        if self.subtitle:
            Annotation.point(
                (self.start + self.end) / 2,
                y_offset + self.height,
                self.subtitle,
                va="bottom",
                text_size=matplotlib.rcParams["legend.fontsize"],
            ).draw(ax)

        if self.xlabel:
            xcoord = (
                (self.start, self.end, y_offset + self.height / 3)
                if self.ylabel
                else (self.start, self.end, y_offset + self.height / 3)
            )
            Annotation.horizontal(*xcoord, text=self.xlabel).draw(ax)
        if self.ylabel:
            ycoord = (
                (
                    y_offset,
                    y_offset + self.height,
                    self.start + (self.end - self.start) * 2 / 3,
                )
                if self.xlabel
                else (y_offset, y_offset + self.height, (self.start + self.end) / 2)
            )
            Annotation.vertical(*ycoord, self.ylabel).draw(ax)

        return self

    def sweep_height(
        self: _Elm,
        points: int = 10,
        data_index: Optional[int] = None,
        start_color: Optional[str] = None,
        start_alpha: Optional[float] = None,
    ) -> _Elm:
        data_index = self._check_data_index(data_index)
        data = self.dataset[0]
        final_alpha = data.style.get("alpha", 1) if data.style is not None else 1
        start_alpha = start_alpha if start_alpha is not None else final_alpha
        for i in range(points - 1, 0, -1):
            color = start_color if start_color is not None else None
            opacity = start_alpha + (final_alpha - start_alpha) * (i / points)
            self.attach_data(
                data.copy()
                .set(height=i / points)
                .update_style(color=color, alpha=opacity)
            )
        return self

    def annotation_to(self: _Elm, elm_to: Union[float, "Element"]) -> _Elm:

        return self

    def copy(self) -> "Element":
        return deepcopy(self)

    def __str__(self) -> str:
        return f"{self.__class__.__name__} : {self.name or self.title} ({self.start}, {self.end})"

    def __repr__(self) -> str:
        return self.__str__()

    @classmethod
    def Gaussian(
        cls,
        start: Optional[Union[float, "Element"]] = None,
        end: Optional[float] = None,
        **kwargs,
    ) -> "Element":
        return cls(start, end, **kwargs).attach_func(
            lambda x: np.exp(-((x - 0.5) ** 2) / 0.1)
        )

    @classmethod
    def ExpFilter(
        cls,
        start: Optional[Union[float, "Element"]] = None,
        end: Optional[float] = None,
        height: float = 1,
        filter_duration=0.1,
        **kwargs,
    ) -> "Element":
        return (
            cls(start, end, height=height, **kwargs)
            .attach_func(
                lambda x: 1 - np.exp(-x / filter_duration**2), end=filter_duration
            )
            .attach_func(
                lambda x: np.exp(-(x - 1 + filter_duration) / filter_duration**2),
                start=1 - filter_duration,
            )
        )
