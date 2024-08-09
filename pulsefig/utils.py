from typing import TYPE_CHECKING, Optional, Tuple, Union

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from .element import Element
    from .line import Line, LineEnsemble


def get_start_end_time(
    obj: "Union[Element, Line, LineEnsemble]",
) -> "Tuple[Optional[float], Optional[float]]":
    if hasattr(obj, "start") and hasattr(obj, "end"):  # isinstance(obj, Element):
        return obj.start, obj.end  # type: ignore
    elif hasattr(obj, "elements"):  # isinstance(obj, Line):
        if not obj.elements:  # type: ignore
            return None, None

        start = obj.elements[0].start or 0  # type: ignore
        end = obj.elements[0].end or 0  # type: ignore

        for elm in obj.elements:  # type: ignore
            start = min(start, elm.start) if elm.start is not None else start
            end = max(end, elm.end) if elm.end is not None else end
        return start, end
    elif hasattr(obj, "lines"):  # isinstance(obj, LineEnsemble):
        if not obj.lines:  # type: ignore
            return None, None

        start, end = get_start_end_time(obj.lines[0])  # type: ignore
        if start is None or end is None:
            raise ValueError("Start or end time is None")
        for line in obj.lines:  # type: ignore
            line_start, line_end = get_start_end_time(line)
            if line_start is not None:
                start = min(start, line_start)
            if line_end is not None:
                end = max(end, line_end)
        return start, end

    raise ValueError(f"Unknown object type: {type(obj)}")


def arrow_between_elements(
    ax: "Axes", elm1: "Element", elm2: "Element", text: str = "", height: float = 0.5
):
    arrow_between_coordinates(
        ax,
        (elm1.end, elm1.y_offset + elm1.height * height),
        (elm2.start, elm2.y_offset + elm2.height * height),
        text,
    )


def arrow_between_coordinates(
    ax: "Axes", coord1, coord2, text, ha="center", va="bottom"
):
    ax.annotate(
        "",
        xy=(coord1[0], coord1[1]),
        xycoords="data",
        xytext=(coord2[0], coord2[1]),
        textcoords="data",
        arrowprops=dict(arrowstyle="<->"),
    )
    if text:
        ax.annotate(
            text,
            ((coord1[0] + coord2[0]) / 2, (coord1[1] + coord2[1]) / 2),
            ha=ha,
            va=va,
        )
