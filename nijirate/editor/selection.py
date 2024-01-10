from typing import List, Callable, Optional

import pygame

from editor.view.viewcomponents import ViewComponent

BOUNDING_COLOUR = (250, 250, 250)
BOUNDING_OUTLINE_COLOUR = (0, 0, 255)
BOUNDING_CORNER_SIZE = 40
BOUNDING_PADDING_PX = 0

SELECTION_COLOUR = (0, 100, 255)


def get_rect_from_pts(a, b, c, d):
    x1 = min(a, c)
    x2 = max(a, c)
    y1 = min(b, d)
    y2 = max(b, d)
    w, h = x2 - x1, y2 - y1
    return pygame.Rect(x1, y1, w, h)


class DragHandler:
    def __init__(self, on_drag: Callable[[float, float, float, float], None], rect=None):
        self.rect = rect
        self.on_press: Optional[Callable[[None], None]] = None
        self.on_release: Optional[Callable[[None], None]] = None
        self.on_drag = on_drag
        self.dragging = False
        self._initx = 0
        self._inity = 0
        self._mousedowned = False

    def mousedown(self):
        mx, my = pygame.mouse.get_pos()
        if self.rect is not None and not self.rect.collidepoint(mx, my):
            return True
        if self.on_press:
            self.on_press()
        self.dragging = True
        self._initx, self._inity = mx, my
        self._mousedowned = True
        return False

    def mouseup(self):
        if not self._mousedowned:
            return
        self._mousedowned = False
        if self.on_release is not None:
            self.on_release()
        self.dragging = False

    def update(self):
        if self.on_drag is None:
            return
        if self.dragging:
            mx, my = pygame.mouse.get_pos()
            self.on_drag(self._initx, self._inity, mx, my)
            return
        return


class BoundingBoxHandler:
    """
    Handles selection of objects
    """

    class ScaleBox:
        def __init__(self, right: bool, top: bool, parent):
            self.right = right
            self.top = top
            self.parent = parent
            self.dh = DragHandler(self.on_drag, self.get_rect())

        def on_drag(self):
            print("e")

        def get_rect(self):
            return self._get_corner_rect(self.right, self.top)

        def updatesize(self):
            self.dh.rect = self.get_rect()

        def mouseup(self):
            self.dh.mouseup()

        def mousedown(self):
            return self.dh.mousedown()

        def _get_corner_rect(self, right: bool, top: bool) -> pygame.Rect:
            cw, ch = BOUNDING_CORNER_SIZE, BOUNDING_CORNER_SIZE
            if self.parent.rect.w > cw:
                x = self.parent.rect.right - cw if right else self.parent.rect.left
            else:
                x = self.parent.rect.right if right else self.parent.rect.left - cw
            if self.parent.rect.h > ch:
                y = self.parent.rect.top if top else self.parent.rect.bottom - ch
            else:
                y = self.parent.rect.top - ch if top else self.parent.rect.bottom
            return pygame.Rect(x, y, cw, ch)

        def draw(self, surface):
            pygame.draw.rect(surface, BOUNDING_COLOUR, self.get_rect(), width=1)

    def __init__(self):
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.subjects = []
        self.initrects = []
        self.dh = DragHandler(self.on_drag, self.rect)
        self.dh.on_press = self.on_press
        self.dh.on_release = self.on_release
        self.scaleboxes = [
            self.ScaleBox(True, True, self),
            self.ScaleBox(True, False, self),
            self.ScaleBox(False, True, self),
            self.ScaleBox(False, False, self),
        ]

    def on_release(self):
        self.initrects.clear()

    def on_press(self):
        for s in self.subjects:
            self.initrects.append(s.rect)

    def on_drag(self, initx, inity, x, y):
        for i, s in enumerate(self.subjects):
            # displace the subject using offsets
            offsetx = initx - self.initrects[i].x
            offsety = inity - self.initrects[i].y
            # use minmaxing to draw the selection rectangle
            (minx, miny), _ = self._minmax()
            nr = pygame.Rect(minx, miny, self.rect.w, self.rect.h)
            # TODO: clamping
            s.set_pos(x - offsetx, y - offsety)
            self.set_rect(nr)

    def set_subjects(self, components: List[ViewComponent]):
        self.subjects = components
        (minx, miny), (maxx, maxy) = self._minmax()
        w = maxx - minx
        h = maxy - miny
        self.set_rect(pygame.Rect(minx, miny, w, h).inflate(BOUNDING_PADDING_PX, BOUNDING_PADDING_PX))

    def set_rect(self, rect):
        self.rect = rect
        self.dh.rect = rect
        for s in self.scaleboxes:
            s.updatesize()

    def _minmax(self):
        minx, miny = (9000, 9000)
        maxx, maxy = (-1, -1)
        for s in self.subjects:
            minx = min(minx, s.rect.left)
            maxx = max(maxx, s.rect.right)
            miny = min(miny, s.rect.top)
            maxy = max(maxy, s.rect.bottom)
        return (minx, miny), (maxx, maxy)

    def mouseup(self):
        self.dh.mouseup()
        [x.mouseup() for x in self.scaleboxes]

    def mousedown(self):
        return self.dh.mousedown() or all([x.mousedown() for x in self.scaleboxes])

    def update(self):
        self.dh.update()

    def draw(self, surface):
        if len(self.subjects) == 0:
            return

        # outline
        pygame.draw.rect(surface, BOUNDING_OUTLINE_COLOUR, self.rect, width=1)

        # TODO: scaling with multiple objects
        if len(self.subjects) > 1:
            return

        # corners
        for s in self.scaleboxes:
            s.draw(surface)


class SelectionBoxHandler:
    """
    Handles ux that allows users to generate bounding boxes
    """

    def __init__(self, components, on_select: Callable[[List[ViewComponent]], None]):
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.dh = DragHandler(self.on_drag)
        self.dh.on_release = self.on_release
        self.components = components
        self.on_select = on_select

    def mouseup(self):
        self.dh.mouseup()

    def mousedown(self):
        self.dh.mousedown()

    def update(self):
        self.dh.update()

    def on_release(self):
        # search components for intersections
        comps = []
       ## ensure a minimum size to allow single clicking components
       #if self.rect.w * self.rect.h == 0:
       #    mx, my = pygame.mouse.get_pos()
       #    self.rect = pygame.Rect(mx, my, 1, 1)
        for c in self.components:
            if self.rect.colliderect(c.rect):
                comps.append(c)
        self.on_select(comps)
        self.rect = pygame.Rect(0, 0, 0, 0)

    def on_drag(self, initx, inity, x, y):
        self.rect = get_rect_from_pts(initx, inity, x, y)

    def draw(self, surface):
        if not self.dh.dragging:
            return
        surf = pygame.Surface((self.rect.w, self.rect.h))
        surf.set_alpha(128)
        surf.fill(SELECTION_COLOUR)
        surface.blit(surf, (self.rect.x, self.rect.y))
