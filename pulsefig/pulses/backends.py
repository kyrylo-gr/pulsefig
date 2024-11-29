from typing import TYPE_CHECKING, Optional

from matplotlib.axes import Axes

if TYPE_CHECKING:
    from .element import FillData, PlotStyle


class DefaultBackend:
    def draw_fill_data(
        self,
        obj: "FillData",
        ax: "Axes",
        start: float,
        end: float,
        offset_y: float,
        style: Optional["PlotStyle"] = None,
    ):
        if style is None:
            style = {}
        if obj.style is not None:
            style.update(obj.style)

        ax.fill_between(
            obj.x * (end - start) + start,
            obj.height_points * obj.height + offset_y,  # type: ignore
            offset_y,
            **style,
        )
