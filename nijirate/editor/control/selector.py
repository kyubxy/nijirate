import math
from abc import ABC, abstractmethod
from typing import Optional

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


class Mode(ABC):
    @abstractmethod
    def mousepressed(self, pos):
        pass

    @abstractmethod
    def mousemotion(self, initpos, pos):
        pass

    @abstractmethod
    def mouseup(self, initpos, pos):
        pass


class TransformMode(Mode):
    def __init__(self, state: State):
        self.state = state
        self.initcompspos = []

    def mousepressed(self, pos):
        self.initcompspos.clear()
        for c in self.state.get_selected():
            self.initcompspos.append((c.x, c.y))

    def mousemotion(self, initpos, pos):
        for i, c in enumerate(self.state.get_selected()):
            mx, my = pos
            isx, isy = self.initcompspos[i]
            ox, oy = (initpos[0] - isx, initpos[1] - isy)
            c.x = mx - ox
            c.y = my - oy

    def mouseup(self, initpos, pos):
        pass


class SelectMode(Mode):
    def __init__(self, state: State):
        self.state = state

    def mousepressed(self, pos):
        pass

    def mousemotion(self, initpos, pos):
        rect = get_rect_from_pts(initpos, pos)
        self.state.set_selected_box(rect)

    def mouseup(self, initpos, pos):
        acc = []
        for node in self.state.get_scenegraph():
            if get_component_rect(node).colliderect(get_rect_from_pts(initpos, pos)):
                acc.append(node)
        self.state.set_selected(acc)
        self.state.set_selected_box(pygame.Rect(0, 0, 0, 0))


def _dist(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


class Selector(MouseListener):
    # TODO: node search is O(n), reduce to O(log(n))

    def __init__(self, state: State):
        super().__init__()
        self.initpos = None
        self.inmotion = False
        self.pressed = False
        self.state = state
        self.sm = SelectMode(self.state)
        self.tm = TransformMode(self.state)
        self.mode: Optional[Mode] = None

    def mousedown(self, pos):
        super().mousedown(pos)
        self.pressed = True
        self.initpos = pos
        # never allow selecting multiple when already inside a component
        # NOTE: start with singleton selection immediately after mouse down
        selected = self.do_singleton_selection(pos)
        if selected is None:
            # didn't mouse down on anything -> open selection box
            self.mode = self.sm
        else:
            # moused down on something, select it and prepare for further transformations
            self.state.set_selected([selected])
            self.mode = self.tm
        self.mode.mousepressed(pos)

    def mousemotion(self, pos):
        if self.initpos is None:
            return
        if self.pressed and _dist(self.initpos, pos) < MINIMUM_ACTIONABLE_DISTANCE and not self.inmotion:
            return
        if self._is_invalidated():
            return
        self.inmotion = True
        self.mode.mousemotion(self.initpos, pos)

    def mouseup(self, pos) -> None:
        self.pressed = False
        self.inmotion = False
        if self._is_invalidated():
            return
        self.mode.mouseup(self.initpos, pos)
        self._invalidate()

    def do_singleton_selection(self, pos) -> Optional[Component]:
        # TODO: singleton selection always takes the topmost element,
        #  make it cycle elements on successive clicks
        for node in self.state.get_scenegraph():
            if get_component_rect(node).collidepoint(pos):
                return node
        return None

    def _is_invalidated(self):
        return self.initpos is None and self._mode is None

    def _invalidate(self):
        self.initpos = None
        self._mode = None
