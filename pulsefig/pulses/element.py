import logging
from copy import deepcopy
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Tuple, TypeVar, Union

import numpy as np
from matplotlib import patches

from ..annotate import _TEXT_TYPE, Annotation
from ..styles import (
    _STYLE_NAMES,
    combine_style_and_kwargs,
    combine_styles,
    get_final_style,
)
from ..utils import remove_prefix_from_dict
from ..variables import UnsetParameter
from .base import AnnotationBase, StyleBase

if TYPE_CHECKING:
    from matplotlib.axes import Axes

_Elm = TypeVar("_Elm", bound="_Element")
_Data = TypeVar("_Data", bound="ElementData")

LINE_PLOT_KW = [
    "linewidth",
    "lw",
    "linestyle",
    "ls",
    "color",
    "alpha",
    "zorder",
]


class ElementData(StyleBase):
    height: float = 1.0
    height_points: np.ndarray
    x: np.ndarray
    _length: int = 100

    def __init__(self, height: float = 1.0, x: Optional[np.ndarray] = None):
        self.height = height
        self.height_points = np.ones(self._length)
        self.height_points[0] = 0
        self.height_points[-1] = 0
        self.x = np.linspace(0, 1, self._length) if x is None else x
        self.style = {}

    def _get_right_x(
        self, x: Optional[np.ndarray], start: float, end: float
    ) -> Tuple[np.ndarray, int, int]:
        if x is None:
            x = self.x
        start_index: int = np.searchsorted(x, start) if start != 0 else 0  # type: ignore
        end_index: int = np.searchsorted(x, end, side="right") if end != 1.0 else len(x)  # type: ignore

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

    def copy(self) -> "ElementData":
        new_data = ElementData(self.height, self.x)
        new_data.height_points = self.height_points.copy()
        new_data.style = self.style.copy()
        return new_data

    def draw(
        self: _Data,
        ax: "Axes",
        start: float,
        end: float,
        offset_y: float,
        style: Optional[dict] = None,
        height: float = 1,
    ) -> _Data:
        style = get_final_style(style, self.style)
        height = height * self.height

        if style.get("fill", False):
            ax.fill_between(
                self.x * (end - start) + start,
                self.height_points * height + offset_y,  # type: ignore
                offset_y,
                **remove_prefix_from_dict(style, "fill."),
            )
        if style.get("contour", False):
            ax.plot(
                self.x * (end - start) + start,
                self.height_points * height + offset_y,  # type: ignore
                **remove_prefix_from_dict(style, "contour."),
            )

        return self


class _Element(StyleBase, AnnotationBase):
    start: float = UnsetParameter()  # type: ignore
    end: float = UnsetParameter()  # type: ignore
    duration: float = UnsetParameter()  # type: ignore
    delay: float = 0
    height: float = 1

    y_offset: float = UnsetParameter()  # type: ignore
    style: dict
    # y_index: int = 0

    _length: int = 100

    def __init__(
        self,
        start: Optional[Union[float, "_Element"]] = None,
        end: Optional[float] = None,
        *,
        duration: Optional[float] = None,
        delay: float = 0,
        height: float = 1,
        name: Optional[str] = None,
    ):
        # if start is None:
        #     raise NotImplementedError("Start time must be specified")
        style = get_final_style()
        element_unit = style.get("element.unit", 1)

        if isinstance(start, _Element):
            start = start.end / element_unit

        if start is not None and delay != 0:
            start = start + delay

        self.start = start * element_unit  # type: ignore
        self.delay = delay * element_unit

        if end is None:
            if duration is None:
                raise ValueError("End time or duration must be specified")
            self.duration = duration * element_unit
            end = (start + duration) if start is not None else None

        self.end = end * element_unit  # type: ignore

        self.height = height * style.get("element.height", 1)
        self.dataset = [ElementData()]
        self.name = name
        self.annotations = []
        self.style = {}

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
        style: Optional[Union[_STYLE_NAMES, Dict[str, Any]]] = None,
        data_index: Optional[int] = None,
        **kwargs,
    ) -> _Elm:
        style = combine_style_and_kwargs(style, **kwargs)

        if data_index is None:
            self.style.update(style)
        else:
            self.dataset[data_index].update_style(style)
        return self

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
        data: Union[np.ndarray, ElementData],
        x: Optional[np.ndarray] = None,
        start: float = 0,
        end: float = 1,
        data_index: Optional[int] = None,
    ) -> _Elm:
        if isinstance(data, ElementData):
            self.dataset.append(data)
            return self
        data_index = self._check_data_index(data_index)
        self.dataset[data_index].attach_data(data, x, start, end)
        return self

    def predraw(
        self: _Elm,
        possible_start: Optional[float] = None,
        y_offset: Optional[float] = None,
    ) -> _Elm:
        if y_offset is not None:
            self.y_offset = y_offset
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
        style: Optional[dict] = None,
        y_offset: Optional[float] = None,
        # y_index: int = 0,
    ) -> _Elm:
        if self.start is None or self.end is None:
            raise ValueError(
                "Start or end time is None. Cannot draw element. Call predraw() first"
            )
        if y_offset is not None:
            self.y_offset = y_offset
        # self.y_index = y_index
        style = combine_styles(self.style, style)

        for data in self.dataset:
            data.draw(
                ax,
                start=self.start,
                end=self.end,
                offset_y=self.y_offset,
                style=style,
                height=self.height,
            )

        self._draw_annotations(ax, style=style)

        return self

    def sweep_height(
        self: _Elm,
        points: int = 10,
        data_index: Optional[int] = None,
        start_color: Optional[str] = None,
        start_alpha: Optional[float] = None,
        final_height: float = 0.0,
    ) -> _Elm:
        data_index = self._check_data_index(data_index)
        data = self.dataset[0]
        final_alpha = data.style.get("alpha", 1.0)
        start_alpha = start_alpha if start_alpha is not None else final_alpha
        for i in range(points - 1, 0, -1):
            color = start_color if start_color is not None else None
            opacity = start_alpha + (final_alpha - start_alpha) * (i / points)
            self.attach_data(
                data.copy()
                .set(height=(i / points) * (1 - final_height) + final_height)
                .update_style(color=color, alpha=opacity)
            )
        return self

    def annotation_to(
        self: _Elm,
        elm_to: "_Element",
        text: str,
        x_start: Optional[float] = None,
        x_end: Optional[float] = None,
        y1: Optional[float] = None,
        y2: Optional[float] = None,
        **kwargs,
    ) -> _Elm:
        y2 = elm_to.y_offset * (self.y_offset > elm_to.y_offset) + elm_to.y_offset * (
            self.y_offset <= elm_to.y_offset
        )
        y1 = (self.y_offset >= elm_to.y_offset) * self.height * 0.6 + self.y_offset
        assert self.start is not None
        assert self.end is not None
        assert elm_to.start is not None
        assert elm_to.end is not None

        x_start = self.end if self.end < elm_to.start else self.start
        x_end = elm_to.start if self.end < elm_to.start else elm_to.end

        self.attach_annotations(
            Annotation.line(x_end, y1, x_end, y2, color="k", **kwargs),
            Annotation.horizontal(start=x_start, end=x_end, y=y1, text=text, **kwargs),
        )

        return self

    def set_ylabel(
        self: _Elm,
        text: str,
        xpos: float = 0.5,
        ypos: float = 0.5,
        start: float = 0,
        end: float = 1,
        ha: str = "left",
        text_size: Optional[float] = None,
        color: Optional[str] = None,
        _group: str = "ylabel",
    ) -> _Elm:
        self.del_annotation_group(_group)

        coord_line = (
            self.y_offset + self.height * start,
            self.y_offset + self.height * end,
            self.start + (self.end - self.start) * xpos,
        )
        coord_text = (
            self.start + (self.end - self.start) * xpos,
            self.y_offset + self.height * ypos,
        )
        self.attach_annotations(
            Annotation.vertical(*coord_line),
            Annotation.point(
                *coord_text,
                text,
                ha=ha,
                text_size=text_size,
                color=color,
            ),
            group=_group,
        )
        return self

    def set_xlabel(
        self: _Elm,
        text: str,
        xpos: float = 0.5,
        ypos: float = 0.33,
        start: float = 0,
        end: float = 1,
        va: str = "bottom",
        text_size: Optional[float] = None,
        color: Optional[str] = None,
        _group: str = "xlabel",
    ) -> _Elm:
        self.del_annotation_group(_group)

        coord = (
            self.start + (self.end - self.start) * start,
            self.start + (self.end - self.start) * end,
            self.y_offset + self.height * ypos,
        )

        coord_text = (
            self.start + (self.end - self.start) * xpos,
            self.y_offset + self.height * ypos,
        )

        self.attach_annotations(
            Annotation.horizontal(*coord),
            Annotation.point(
                *coord_text,
                text,
                va=va,
                text_size=text_size,
                color=color,
            ),
            group=_group,
        )
        return self

    def set_title(
        self: _Elm,
        text: _TEXT_TYPE,
        xpos: float = 0.5,
        ypos: float = 0.5,
        va: str = "center",
        text_size: Optional[float] = None,
        color: Optional[str] = None,
        _group: str = "title",
    ) -> _Elm:
        self.del_annotation_group(_group)

        self.attach_annotations(
            Annotation.point(
                self.start + (self.end - self.start) * xpos,
                self.y_offset + self.height * ypos,
                text,
                va=va,
                text_size=text_size,
                color=color,
            ),
            group=_group,
        )
        return self

    def set_subtitle(
        self: _Elm,
        text: str,
        xpos: float = 0.5,
        ypos: float = 1,
        va: str = "bottom",
        text_size: Optional[float] = None,
        color: Optional[str] = None,
        _group: str = "subtitle",
    ) -> _Elm:
        return self.set_title(
            text=text,
            xpos=xpos,
            ypos=ypos,
            va=va,
            text_size=text_size,
            color=color,
            _group=_group,
        )

    def copy(self) -> "_Element":
        return deepcopy(self)

    def __str__(self) -> str:
        return f"{self.__class__.__name__} : {self.name} ({self.start}, {self.end})"

    def __repr__(self) -> str:
        return self.__str__()

    @classmethod
    def Gaussian(
        cls,
        *args,
        **kwargs,
    ) -> "_Element":
        return cls(*args, **kwargs).attach_func(
            lambda x: np.exp(-((x - 0.5) ** 2) / 0.1)
        )

    @classmethod
    def ExpFilter(
        cls,
        start: Optional[Union[float, "_Element"]] = None,
        end: Optional[float] = None,
        height: float = 1,
        filter_duration=0.1,
        **kwargs,
    ) -> "_Element":
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


class Pulse(_Element):
    pass


class Element(Pulse):
    def __init__(self, *args, **kwargs):
        logging.warning(
            "Element is deprecated and because general type."
            "It will be removed in the next release. Use Pulse instead."
        )
        super().__init__(*args, **kwargs)


class Gate(_Element):
    def __init__(
        self,
        start: Optional[Union[float, "_Element"]] = None,
        end: Optional[float] = None,
        *,
        duration: Optional[float] = None,
        delay: float = 0,
        height: float = 0.4,
        name: Optional[str] = None,
    ):
        super().__init__(
            start, end, duration=duration, delay=delay, height=height, name=name
        )

    def draw(
        self: _Elm,
        ax: "Axes",
        *,
        style: Optional[dict] = None,
        y_offset: Optional[float] = None,
        # y_index: int = 0,
    ) -> _Elm:
        if self.start is None or self.end is None:
            raise ValueError(
                "Start or end time is None. Cannot draw element. Call predraw() first"
            )
        if y_offset is not None:
            self.y_offset = y_offset
        # self.y_index = y_index
        style = combine_styles(self.style, style)

        for data in self.dataset:
            data.draw(
                ax,
                self.start,
                self.end,
                self.y_offset,
                style,
                height=self.height,
            )
            data.draw(
                ax,
                self.start,
                self.end,
                self.y_offset,
                style,
                height=-self.height,
            )

        self._draw_annotations(ax, style=style)

        return self

    def set_title(
        self: _Elm,
        text: _TEXT_TYPE,
        xpos: float = 0.5,
        ypos: float = 0,
        va: str = "center",
        text_size: float | None = None,
        color: str | None = None,
        _group: str = "title",
    ) -> _Elm:
        return super().set_title(text, xpos, ypos, va, text_size, color, _group)

    @classmethod
    def Readout(
        cls,
        start: Optional[Union[float, "_Element"]] = None,
        end: Optional[float] = None,
        *,
        duration: Optional[float] = None,
        delay: float = 0,
        height: float = 0.4,
        name: Optional[str] = None,
        color: str = "black",
        mutation_scale: float = 0.0,
        **kwargs,
    ):
        readout = cls(
            start, end, duration=duration, delay=delay, height=height, name=name
        )

        def draw_measure(ax: "Axes", x0, y0, arrow_radius_ratio=1.5, **func_kwargs):
            radius = (readout.end - readout.start) / 4
            theta = np.linspace(0, np.pi, 100)
            arc_x = x0 + radius * np.cos(theta)
            arc_y = y0 + radius * np.sin(theta) - radius / 2
            arrow_angle = np.pi / 6
            if mutation_scale == 0:
                ax.plot(
                    [x0, x0 + arrow_radius_ratio * radius * np.cos(arrow_angle)],
                    [
                        y0 - radius / 2,
                        y0
                        + arrow_radius_ratio * radius * np.sin(arrow_angle)
                        - radius / 2,
                    ],
                    color=color,
                    **kwargs,
                )
            else:
                ax.add_patch(
                    patches.FancyArrowPatch(
                        (x0, y0 - radius / 2),
                        (
                            x0 + arrow_radius_ratio * radius * np.cos(arrow_angle),
                            y0
                            + arrow_radius_ratio * radius * np.sin(arrow_angle)
                            - radius / 2,
                        ),
                        arrowstyle="->",
                        shrinkA=0,
                        shrinkB=0,
                        color=color,
                        mutation_scale=mutation_scale,
                        **kwargs,
                    )
                )
            # kwargs.pop("mutation_scale")
            ax.plot(arc_x, arc_y, color=color, **kwargs)

        readout.set_title(draw_measure)

        return readout
