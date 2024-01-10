import math
from enum import Enum
from typing import Optional, List

import pygame.mouse

from editor.control.mouselistener import MouseListener
from editor.model.component import get_component_rect, Component
from editor.model.state import State

MINIMUM_ACTIONABLE_DISTANCE = 4


def get_rect_from_pts(p1, p2):
    a, b = p1
    c, d = p2
    x1 = min(a, c)
    x2 = max(a, c)
    y1 = min(b, d)
    y2 = max(b, d)
    w, h = x2 - x1, y2 - y1
    return pygame.Rect(x1, y1, w, h)


class TransformMode(MouseListener):

    def mousedown(self, pos):
        pass

    def mousemotion(self, pos):
        pass

    def mouseup(self, pos) -> None:
        pass


class SelectMode(MouseListener):

    def mousemotion(self, pos):
        pass

    def mouseup(self, pos) -> None:
        pass

    def mousedown(self, pos):
        pass


class SelectionMode(Enum):
    """
    What should happen when the user drags their cursor
    """
    TRANFORM = 0
    SELECT = 1


class Selector(MouseListener):
    # TODO: node search is O(n), reduce to O(log(n))

    def __init__(self, state: State):
        super().__init__()
        self.state = state
        self.initpos = None
        self.nodeoffset = (0, 0)
        self.mode: Optional[SelectionMode] = None
        self.inmotion = False
        self.pressed = False

    def mousedown(self, pos):
        super().mousedown(pos)
        self.pressed = True
        # only mousedown can validate state
        self.initpos = pos
        # never allow selecting multiple when already inside a component
        for node in self.state.get_scenegraph():
            if get_component_rect(node).collidepoint(pos):
                self.mode = SelectionMode.TRANFORM
                self.nodeoffset = (pos[0] - node.x, pos[1] - node.y)
                self.state.set_selected(self.do_singleton_selection(pos))
            else:
                self.mode = SelectionMode.SELECT

    def mousemotion(self, pos):
        if self.initpos is None:
            return
        if self.pressed and math.hypot(self.initpos[0] - pos[0], self.initpos[1] - pos[1]) < MINIMUM_ACTIONABLE_DISTANCE and not self.inmotion:
            return
        self.inmotion = True
        if self._is_invalidated():
            return
        elif self.mode == SelectionMode.TRANFORM:
            for c in self.state.get_selected():
                mx, my = pos
                ox, oy = self.nodeoffset
                c.x = mx - ox
                c.y = my - oy
        elif self.mode == SelectionMode.SELECT:
            rect = get_rect_from_pts(self.initpos, pos)
            self.state.set_selected_box(rect)

    def mouseup(self, pos) -> None:
        self.pressed = False
        self.inmotion = False
        if self._is_invalidated():
            return  # don't operate on invalidated states
        elif self.mode == SelectionMode.TRANFORM:
            pass
        elif self.mode == SelectionMode.SELECT:
            self.state.set_selected(self.do_multi_selection(get_rect_from_pts(self.initpos, pos)))
        self._invalidate()
        self.state.set_selected_box(pygame.Rect(0, 0, 0, 0))

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

    def _is_invalidated(self):
        return self.initpos is None and self.mode is None

    def _invalidate(self):
        self.initpos = None
        self.mode = None
