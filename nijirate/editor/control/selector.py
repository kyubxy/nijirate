import math
from abc import ABC
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


class TranslateMode(Mode):
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


class ScaleMode(Mode):
    def __init__(self, state:State):
        self._state: State = state
        self.initrect = None

    # TODO: use the selected list directly when implementing multiscale
    def __get_one(self):
        return self._state.get_selected()[0]

    def mousepressed(self, pos):
        one = self.__get_one()
        self.initrect = pygame.Rect(one.x, one.y, one.w, one.y)

    def mousemotion(self, initpos, pos):
        if self.initrect is None:
            return  # malformed state - seeya later!
        mx, my = pos
        #ox, oy = (initpos[0] - self.initrect.right, initpos[1] - self.initrect.bottom)
        ox, oy = self.initrect.right, self.initrect.bottom
        self.__get_one().w = mx - ox
        self.__get_one().h = my - oy
        self.initrect = None


class SelectMode(Mode):
    def __init__(self, state: State):
        self._state = state

    def mousemotion(self, initpos, pos):
        rect = get_rect_from_pts(initpos, pos)
        self._state.set_selection_box(rect)

    def mouseup(self, initpos, pos):
        # NOTE: putting this in mousemotion allows for instant selection of
        # components which might be considered better ux but at a slightly higher performance cost
        # (which does scale in the number of available components)
        acc = []
        for node in self._state.get_scenegraph():
            if get_component_rect(node).colliderect(get_rect_from_pts(initpos, pos)):
                acc.append(node)
        self._state.set_selected(acc)
        self._state.set_selection_box(pygame.Rect(0, 0, 0, 0))


class Selector(MouseListener):
    # TODO: node search is O(n), reduce to O(log(n))

    def __init__(self, state: State):
        super().__init__()

        def get_checks():
            tm = TranslateMode(state)
            return [
                (self.check_scale, ScaleMode(state)),
                (self.check_translate, tm),
                (self.check_multitranslate, tm),  # TODO: multi move only when actual elements clicked

                # pick this as the sane default - didn't mouse down on anything -> open selection box
                (lambda _: True, SelectMode(state)),
            ]

        self._initpos = None
        self._inmotion = False
        self._state = state
        self.checks = get_checks()
        self._mode: Optional[Mode] = None

    def check_scale(self, pos) -> bool:
        bb = self._state.get_boundingbox()
        if bb is None:
            return False
        for box in bb.get_size_boxes():
            if box.get_rect().collidepoint(pos):
                return True
        return False

    def check_translate(self, pos) -> bool:
        bb = self._state.get_boundingbox()
        # bb exists, immediately begin moving it
        return bb is not None and bb.get_rect().collidepoint(pos)

    def check_multitranslate(self, pos) -> bool:
        anysel = self._do_singleton_selection(pos)
        if anysel is not None:
            # moused down on something, select it and prepare for further transformations
            self._state.set_selected([anysel])
            return True
        return False

    def mousedown(self, pos):
        super().mousedown(pos)
        self._initpos = pos
        self._set_mode(pos)
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

    def _set_mode(self, pos):
        for (pred, mode) in self.checks:
            if pred(pos):
                self._mode = mode
                print(self._mode)
                return

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
