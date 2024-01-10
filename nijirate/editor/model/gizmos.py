from abc import ABC, abstractmethod
from typing import List, Optional

import pygame

from editor.model.component import Component, get_component_rect


class GizmoVisitor(ABC):
    @abstractmethod
    def visit_boundingbox(self, bb):
        pass

    @abstractmethod
    def visit_scalebox(self, sc):
        pass


class GizmoElement(ABC):
    @abstractmethod
    def accept(self, visitor: GizmoVisitor):
        pass


def _minmax(components: List[Component]):
    minx, miny = (9000, 9000)  # TODO: do something better than this
    maxx, maxy = (-1, -1)
    for c in components:
        rect = get_component_rect(c)
        minx = min(minx, rect.left)
        maxx = max(maxx, rect.right)
        miny = min(miny, rect.top)
        maxy = max(maxy, rect.bottom)
    return (minx, miny), (maxx, maxy)


class BoundingBox(GizmoElement):
    def __init__(self, selected):
        self._selected = selected

    def get_selected(self) -> List[Component]:
        return self._selected

    def get_rect(self) -> pygame.Rect:
        (minx, miny), (maxx, maxy) = _minmax(self.get_selected())
        return pygame.Rect(minx, miny, maxx - minx, maxy - miny)

    def accept(self, visitor: GizmoVisitor):
        visitor.visit_boundingbox(self)


def get_bounding_box(selected) -> Optional[BoundingBox]:
    if len(selected) > 0:
        return BoundingBox(selected)
    else:
        return None


class ScaleBox(GizmoElement):
    def accept(self, visitor: GizmoVisitor):
        visitor.visit_scalebox(self)
