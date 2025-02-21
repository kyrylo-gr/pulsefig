# flake8: noqa: F401

from typing import Any, Dict, Literal, Optional, Union

import matplotlib
import yaml

DEFAULT_COLOR = "#0050A0"
DEFAULT_TEXT_OFFSET = 1.0


class StyleLink:
    def __init__(self, name: str, data: Optional[dict] = None) -> None:
        self.name = name
        self.data = data

    def eval(self, data=None):
        global CURRENT_STYLE  # pylint: disable=W0602
        if data is None:
            data = CURRENT_STYLE
        if self.data is not None and self.name in self.data:
            return self.data[self.name]
        return data[self.name]

    def __repr__(self):
        return f"StyleLink({self.name})"

    def __str__(self):
        return f"StyleLink({self.name})"


DEFAULT_STYLE: Dict[str, Any] = {
    # General
    "color": DEFAULT_COLOR,
    "fontsize": StyleLink("legend.fontsize", matplotlib.rcParams),
    # Annotation
    "annotation.color": StyleLink("color"),
    # Annotation text
    "text.fontsize": StyleLink("fontsize"),
    "text.color": "#000",
    # Level style
    "level.line.color": StyleLink("color"),
    "level.text.fontsize": StyleLink("fontsize"),
    "level.textoffset": DEFAULT_TEXT_OFFSET,
    # Fill style
    "fill": True,
    "fill.color": StyleLink("color"),
    # Contour style
    "contour": False,
    "contour.color": StyleLink("color"),
}

CURRENT_STYLE = DEFAULT_STYLE.copy()


STYLE_MAP: Dict[str, Dict[str, Any]] = {
    "fill": {
        "fill": True,
        "contour": False,
    },
    "contour": {
        "fill": False,
        "contour": True,
    },
}

_STYLE_NAMES = Literal["fill", "contour"]


def update_style(
    *styles: Optional[Union[_STYLE_NAMES, Dict[str, Any]]], **kwargs
) -> Dict[str, Any]:
    global CURRENT_STYLE  # pylint: disable=W0602
    for s in styles:
        if isinstance(s, str):
            s = STYLE_MAP[s].copy()
        if s is None:
            continue
        if not isinstance(s, dict):
            raise ValueError(f"Unknown style: {s}. Must be a dict or a style name.")
        CURRENT_STYLE.update(s)

    if kwargs:
        CURRENT_STYLE.update({k.replace("_", "."): v for k, v in kwargs.items()})

    return CURRENT_STYLE


def update_style_from_file(filename):
    with open(str(filename), "r", encoding="utf-8") as file:
        styles = yaml.safe_load(file)
    update_style(**styles)


def current_style():
    global CURRENT_STYLE  # pylint: disable=W0602
    return CURRENT_STYLE.copy()


def reset_style():
    global CURRENT_STYLE  # pylint: disable=W0603
    CURRENT_STYLE = DEFAULT_STYLE.copy()


def _eval_style(val, data=None):
    if isinstance(val, StyleLink):
        return _eval_style(val.eval(data=data), data)
    return val


def get_style(key: str, style: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
    if key in kwargs:
        return _eval_style(kwargs[key])
    if style is not None and key in style:
        return _eval_style(style[key])
    return _eval_style(CURRENT_STYLE[key])


update_style("fill")


def get_final_style(
    style1: Optional[dict] = None, style2: Optional[dict] = None
) -> dict:

    style = CURRENT_STYLE.copy()
    style = combine_styles(style, style1)
    style = combine_styles(style, style2)
    # if style1 is not None:
    #     style.update(style1)
    # if style2 is not None:
    #     style.update(style2)

    for k, v in style.items():
        if isinstance(v, StyleLink):
            style[k] = _eval_style(v, style)

    return style


def combine_styles(style1: dict, style2: Optional[dict] = None) -> dict:
    style = style1.copy()
    if style2 is not None:
        for k, v in style2.items():
            if isinstance(v, dict) and k in style:
                style[k] = combine_styles(style[k], v)
            else:
                style[k] = style2[k]
    return style


def combine_style_and_kwargs(
    style: Optional[Union[_STYLE_NAMES, Dict[str, Any]]] = None, **kwargs
) -> Dict[str, Any]:
    style = STYLE_MAP[style].copy() if isinstance(style, str) else (style or {})
    if kwargs:
        style = combine_styles(
            style, {k.replace("_", "."): v for k, v in kwargs.items()}
        )
    style = {k: v for k, v in style.items() if v is not None}

    return style
