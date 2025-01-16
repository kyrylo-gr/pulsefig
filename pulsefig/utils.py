from typing import TYPE_CHECKING, List, Optional, Tuple, Union

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from .pulses.element import Element
    from .pulses.line import Line, LineEnsemble


def get_start_end_time(
    obj: "Union[Element, Line, LineEnsemble]",
) -> "Tuple[Optional[float], Optional[float]]":
    if (
        getattr(obj, "start", None) is not None
        and getattr(obj, "end", None) is not None
    ):  # isinstance(obj, Element):
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

        # start, end = get_start_end_time(obj.lines[0])  # type: ignore
        # if start is None or end is None:
        #     raise ValueError("Start or end time is None")
        start, end = None, None
        for line in obj.lines:  # type: ignore
            line_start, line_end = get_start_end_time(line)
            if line_start is not None:
                start = min(start, line_start) if start is not None else line_start
            if line_end is not None:
                end = max(end, line_end) if end is not None else line_end
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


def filter_none(data: Optional[dict] = None, **kwargs) -> dict:
    if data is not None:
        kwargs.update(data)
    return {k: v for k, v in kwargs.items() if v is not None}


def filter_kwargs(names_: List[str], /, data: Optional[dict] = None, **kwargs):
    if data is not None:
        kwargs.update(data)
    return {k: v for k, v in kwargs.items() if k in names_ and v is not None}


def set_kwargs(obj, **kwargs):
    for key, value in kwargs.items():
        if hasattr(obj, f"set_{key}"):
            getattr(obj, f"set_{key}")(value)
        elif hasattr(obj, key):
            setattr(obj, key, value)
        elif hasattr(obj, "style"):
            obj.style[key.replace("_", ".")] = value
        else:
            raise AttributeError(f"Object {obj} has no attribute {key}")
    return obj


def remove_prefix_from_dict(data: dict, prefix: str) -> dict:
    # return {k[len(prefix) :]: v for k, v in data.items() if k.startswith(prefix)} | {
    #     k: v for k, v in data.items() if not k.startswith(prefix)
    # }

    return {k[len(prefix) :]: v for k, v in data.items() if k.startswith(prefix)}
