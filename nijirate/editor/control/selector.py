from enum import Enum
from typing import Optional, List

import pygame.mouse

from editor.control.mouselistener import MouseListener
from editor.model.component import get_component_rect, Component
from editor.model.state import State

MINIMUM_SELECTION_AREA = 4


def get_rect_from_pts(p1, p2):
    a, b = p1
    c, d = p2
    x1 = min(a, c)
    x2 = max(a, c)
    y1 = min(b, d)
    y2 = max(b, d)
    w, h = x2 - x1, y2 - y1
    return pygame.Rect(x1, y1, w, h)


class SelectionMode(Enum):
    SINGLETON = 0
    MULTI = 1


class Selector(MouseListener):
    def __init__(self, state: State):
        super().__init__()
        self.state = state
        self.initpos = None
        self.mode: Optional[SelectionMode] = None

    def mousedown(self, pos):
        super().mousedown(pos)
        # only mousedown can validate state
        self.initpos = pos
        self.mode = SelectionMode.SINGLETON  # start off in singleton

    def mousemotion(self, pos):
        if self._is_invalidated():
            return
        rect = get_rect_from_pts(self.initpos, pos)
        if rect.w * rect.h > MINIMUM_SELECTION_AREA:
            self.state.set_selected_box(rect)
            self.mode = SelectionMode.MULTI  # currently drawing a box -> move to multi

    # TODO: node search is O(n), reduce to O(log(n))

    def do_singleton_selection(self, pos) -> List[Component]:
        # TODO: singleton selection always takes the topmost element,
        #  make it cycle elements on successive clicks
        for node in self.state.get_scenegraph():
            if get_component_rect(node).collidepoint(pos):
                return [node]
        return []

    def do_multi_selection(self, rect) -> List[Component]:
        acc = []
        for node in self.state.get_scenegraph():
            if get_component_rect(node).colliderect(rect):
                acc.append(node)
        return acc

    def mouseup(self, pos) -> None:
        if self._is_invalidated():
            return  # don't operate on invalidated states
        if self.mode == SelectionMode.SINGLETON:
            self.state.set_selected(self.do_singleton_selection(pos))
        elif self.mode == SelectionMode.MULTI:
            self.state.set_selected(self.do_multi_selection(get_rect_from_pts(self.initpos, pos)))
        self._invalidate()
        self.state.set_selected_box(pygame.Rect(0, 0, 0, 0))

    def _is_invalidated(self):
        return self.initpos is None and self.mode is None

    def _invalidate(self):
        self.initpos = None
        self.mode = None
