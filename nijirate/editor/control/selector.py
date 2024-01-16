import math
from abc import ABC
from typing import Optional

import pygame.mouse

from editor.control.mouselistener import MouseListener
from editor.model.component import get_component_rect, Component
from editor.model.gizmos import BOUNDING_CORNER_SIZE, Corner
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
    def mousepressed(self, pos, args):
        pass

    def mousemotion(self, initpos, pos):
        pass

    def mouseup(self, initpos, pos):
        pass


class TranslateMode(Mode):
    def __init__(self, state: State):
        self._state = state
        self._initcompspos = []

    def mousepressed(self, pos, args):
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


def get_2pt_rect(pt1: (int, int), pt2: (int, int)) -> (int, int, int, int):
    # this is such a dumb way of moving the variables but i dont care
    pt1x, pt1y = pt1
    pt2x, pt2y = pt2
    pt1_ = min(pt1x, pt2x), min(pt1y, pt2y)
    pt2_ = max(pt1x, pt2x), max(pt1y, pt2y)
    pt1x, pt1y = pt1_
    pt2x, pt2y = pt2_
    return pt1x, pt1y, pt2x - pt1x, pt2y - pt1y


class ScaleMode(Mode):
    def __init__(self, state: State):
        self._state: State = state
        self._initrect = None
        self._corner = None

    # TODO: use the selected list directly when implementing multiscale
    def __get_one(self):
        return self._state.get_selected()[0]

    def mousepressed(self, pos, args):
        one = self.__get_one()
        self._corner = args
        self._initrect = pygame.Rect(one.x, one.y, one.w, one.y)
        print(self._initrect.x, self._initrect.y, self._initrect.w, self._initrect.h)

    def mousemotion(self, initpos, pos):
        if self._initrect is None or self._corner is None:
            return  # malformed state - seeya later!
        #pygame.mouse.set_visible(False)
        mx, my = pos
        irect = self._initrect
        fixedpt = None
        if self._corner == Corner.BOTTOM_RIGHT:
            fixedpt = (irect.left, irect.top)
            fx, fy, fw, fh = get_2pt_rect(fixedpt, (mx, my))
        elif self._corner == Corner.BOTTOM_LEFT:
            fixedpt = (irect.right, irect.top)
            fx, fy, fw, fh = get_2pt_rect(fixedpt, (mx, my))
        elif self._corner == Corner.TOP_LEFT:
            fixedpt = (irect.right, irect.bottom)
            fx, fy, fw, fh = get_2pt_rect((mx, my), fixedpt)
        elif self._corner == Corner.TOP_RIGHT:
            fixedpt = (irect.left, irect.bottom)
            fx, fy, fw, fh = get_2pt_rect((mx, my), fixedpt)

        #fx, fy, fw, fh = get_2pt_rect(fixedpt, (mx, my))
        self.__get_one().x = fx
        self.__get_one().y = fy
        self.__get_one().w = fw
        self.__get_one().h = fh

    def mouseup(self, _, __):
        #pygame.mouse.set_visible(True)
        self._initrect = None
        self._corner = None


# TODO: rotation
class RotateMode(Mode):
    ...


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

    def check_scale(self, pos):
        bb = self._state.get_boundingbox()
        if bb is None:
            return False
        for box in bb.get_size_boxes():
            if box.get_rect().collidepoint(pos):
                return box.get_corner()
        return False

    def check_translate(self, pos):
        bb = self._state.get_boundingbox()
        # bb exists, immediately begin moving it
        return bb is not None and bb.get_rect().collidepoint(pos)

    def check_multitranslate(self, pos):
        anysel = self._do_singleton_selection(pos)
        if anysel is not None:
            # moused down on something, select it and prepare for further transformations
            self._state.set_selected([anysel])
            return True
        return False

    def mousedown(self, pos):
        super().mousedown(pos)
        self._initpos = pos
        args = self._set_mode(pos)
        self._mode.mousepressed(pos, args)

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
        # we are guarenteed that there will always be at least one mode to return
        for (pred, mode) in self.checks:
            args = pred(pos)
            if args:
                self._mode = mode
                print(self._mode)
                return args

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
