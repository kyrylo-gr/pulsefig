from copy import deepcopy
from typing import TYPE_CHECKING, Any, Dict, List, Optional, TypeVar, Union

from ..annotate import Annotation
from ..styles import _STYLE_NAMES, combine_style_and_kwargs
from ..utils import set_kwargs

_S = TypeVar("_S", bound="StyleBase")
_A = TypeVar("_A", bound="AnnotationBase")

if TYPE_CHECKING:
    from matplotlib.axes import Axes


class StyleBase:
    style: Dict[str, Any]

    def set(self: _S, **kwargs) -> _S:
        return set_kwargs(self, **kwargs)

    def copy(self: _S) -> _S:
        return deepcopy(self)

    def update_style(
        self: _S, style: Optional[Union[_STYLE_NAMES, Dict[str, Any]]] = None, **kwargs
    ) -> _S:
        self.style.update(combine_style_and_kwargs(style, **kwargs))
        return self


class AnnotationBase:
    annotations: List[Annotation]

    def attach_annotations(
        self: _A, *annotation: Annotation, group: Optional[str] = None
    ) -> _A:
        if group is not None:
            for a in annotation:
                a.group = group

        self.annotations.extend(annotation)
        return self

    def _draw_annotations(self, ax: "Axes", style: Optional[dict] = None) -> None:
        for a in self.annotations:
            a.draw(ax, style=style)

    def del_annotation_group(self: _A, group: Optional[str]) -> _A:
        self.annotations = [a for a in self.annotations if a.group != group]
        return self
