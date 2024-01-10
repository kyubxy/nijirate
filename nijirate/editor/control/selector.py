import math
from abc import ABC, abstractmethod
from typing import Optional

import pygame.mouse

from editor.control.mouselistener import MouseListener
from editor.model.component import get_component_rect, Component
from editor.model.state import State

MINIMUM_ACTIONABLE_DISTANCE = 4


def _dist(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


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
    def mousepressed(self, pos):
        pass

    def mousemotion(self, initpos, pos):
        pass

    def mouseup(self, initpos, pos):
        pass


class TransformMode(Mode):
    def __init__(self, state: State):
        self._state = state
        self._initcompspos = []

    def mousepressed(self, pos):
        self._initcompspos.clear()
        for c in self._state.get_selected():
            self._initcompspos.append((c.x, c.y))

    def mousemotion(self, initpos, pos):
        for i, c in enumerate(self._state.get_selected()):
            mx, my = pos
            isx, isy = self._initcompspos[i]
            ox, oy = (initpos[0] - isx, initpos[1] - isy)
            c.x = mx - ox
            c.y = my - oy


class SelectMode(Mode):
    def __init__(self, state: State):
        self._state = state

    def mousemotion(self, initpos, pos):
        rect = get_rect_from_pts(initpos, pos)
        self._state.set_selected_box(rect)

    def mouseup(self, initpos, pos):
        # NOTE: putting this in mousemotion allows for instant selection of
        # components which might be considered better ux but at a slightly higher performance cost
        # (which does scale in the number of available components)
        acc = []
        for node in self._state.get_scenegraph():
            if get_component_rect(node).colliderect(get_rect_from_pts(initpos, pos)):
                acc.append(node)
        self._state.set_selected(acc)
        self._state.set_selected_box(pygame.Rect(0, 0, 0, 0))


class Selector(MouseListener):
    # TODO: node search is O(n), reduce to O(log(n))

    def __init__(self, state: State):
        super().__init__()
        self._initpos = None
        self._inmotion = False
        self._state = state
        self._sm = SelectMode(self._state)
        self._tm = TransformMode(self._state)
        self._mode: Optional[Mode] = None

    def mousedown(self, pos):
        super().mousedown(pos)
        self._initpos = pos
        bb = self._state.get_boundingbox()
        # TODO: make it so you can only multi move when you click on the actual elements not just the bounding box
        anysel = self._do_singleton_selection(pos)
        if bb is not None and bb.get_rect().collidepoint(pos):
            # bb exists, immediately begin moving it
            self._mode = self._tm
        elif anysel is not None:
            # moused down on something, select it and prepare for further transformations
            self._state.set_selected([anysel])
            self._mode = self._tm
        else:  # self._do_singleton_selection(pos) is None:
            # pick this as the sane default - didn't mouse down on anything -> open selection box
            self._mode = self._sm
        self._mode.mousepressed(pos)

    def mousemotion(self, pos):
        if self._is_invalidated():
            return
        if _dist(self._initpos, pos) < MINIMUM_ACTIONABLE_DISTANCE and not self._inmotion:
            return
        self._inmotion = True
        self._mode.mousemotion(self._initpos, pos)

    def mouseup(self, pos) -> None:
        self._inmotion = False
        if self._is_invalidated():
            return
        self._mode.mouseup(self._initpos, pos)
        self._invalidate()

    def _do_singleton_selection(self, pos) -> Optional[Component]:
        # TODO: singleton selection always takes the topmost element,
        #  make it cycle elements on successive clicks
        for node in self._state.get_scenegraph()[::-1]:
            if get_component_rect(node).collidepoint(pos):
                return node
        return None

    def _is_invalidated(self):
        return self._initpos is None and self._mode is None

    def _invalidate(self):
        self._initpos = None
        self._mode = None
