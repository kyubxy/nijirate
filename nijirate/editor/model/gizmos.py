from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional

import pygame

from editor.model.component import Component, get_component_rect

BOUNDING_CORNER_SIZE = 40


class GizmoVisitor(ABC):
    @abstractmethod
    def visit_boundingbox(self, bb):
        pass

    # TODO: rulers
    # @abstractmethod
    def visit_ruler(self, rl):
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


class Corner(Enum):
    BOTTOM_LEFT = (0, 0)
    BOTTOM_RIGHT = (1, 0)
    TOP_LEFT = (0, 1)
    TOP_RIGHT = (1, 1)


class BoundingBox(GizmoElement):
    def __init__(self, selected):
        self._selected = selected
        self._sboxes = [
            ScaleBox(self, Corner.TOP_LEFT),
            ScaleBox(self, Corner.TOP_RIGHT),
            ScaleBox(self, Corner.BOTTOM_LEFT),
            ScaleBox(self, Corner.BOTTOM_RIGHT)
        ]

    def get_size_boxes(self):
        return self._sboxes

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


class ScaleBox:
    def __init__(self, parent: BoundingBox, corner: Corner):
        self.parent = parent
        self._corner = corner

    def get_rect(self) -> pygame.Rect:
        (right, top) = self._corner.value
        cw, ch = BOUNDING_CORNER_SIZE, BOUNDING_CORNER_SIZE
        if self.parent.get_rect().w > cw:
            x = self.parent.get_rect().right - cw if right else self.parent.get_rect().left
        else:
            x = self.parent.get_rect().right if right else self.parent.get_rect().left - cw
        if self.parent.get_rect().h > ch:
            y = self.parent.get_rect().top if top else self.parent.get_rect().bottom - ch
        else:
            y = self.parent.get_rect().top - ch if top else self.parent.get_rect().bottom
        return pygame.Rect(x, y, cw, ch)
