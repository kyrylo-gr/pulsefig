from typing import List, Literal, Optional, TypeVar

from ..annotate import Annotation
from ..variables import UnsetParameter

_Lvl = TypeVar("_Lvl", bound="Level")


class Level:
    annotations: List[Annotation]
    style: dict
    x: float = UnsetParameter()  # type: ignore
    y: float = UnsetParameter()  # type: ignore

    def __init__(self, name: str, x: float, y: float, style: Optional[dict] = None):
        self.name = name
        self.annotations = []
        self.style = style or {}
        self.x = x
        self.y = y

    def __str__(self) -> str:
        return f"{self.__class__.__name__} : {self.name}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} : {self.name}"

    def __hash__(self) -> int:
        return hash(self.name)

    def set(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, f"set_{key}"):
                getattr(self, f"set_{key}")(value)
            else:
                setattr(self, key, value)
        return self

    def attach_annotations(
        self: _Lvl, *annotations: Annotation, group: Optional[str] = None
    ) -> _Lvl:
        if group is not None:
            for a in annotations:
                a.group = group
        self.annotations.extend(annotations)
        return self

    def update_style(
        self: _Lvl,
        **kwargs,
    ) -> _Lvl:
        if self.style is None:
            self.style = {}
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        self.style.update(kwargs)  # type: ignore
        return self

    def set_title(
        self: _Lvl, title: str, pos: Literal["top", "bottom", "left", "right"] = "top"
    ) -> _Lvl:
        raise NotImplementedError
        # return self

    #     ha = {"top": "center", "bottom": "center", "left": "left", "right": "right"}[
    #         pos
    #     ]
    #     va = {"top": "bottom", "bottom": "top", "left": "center", "right": "center"}[
    #         pos
    #     ]
    #     x = {"top": 0.5, "bottom": 0.5, "left": 0, "right": 1}[pos]
    #     y = {"top": 1, "bottom": 0, "left": 0.5, "right": 0.5}[pos]

    #     self.attach_annotations(Annotation(text=title, ha=ha, va=va))
