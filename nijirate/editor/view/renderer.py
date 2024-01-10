from typing import List

import pygame

from editor.model.component import ComponentVisitor, Text, VideoHolder, Sprite, Component, get_component_rect

WIREFRAME_OUTLINE_COLOUR = (255, 255, 255)
WIREFRAME_TEXT_COLOUR = (100, 100, 100)
WIREFRAME_TEXT_PADDING = 10

SELECTION_COLOUR = (0, 100, 255)
SELECTION_OPACITY = 128

BOUNDING_OUTLINE_COLOUR = (0, 0, 255)


class ComponentRenderer(ComponentVisitor):
    def __init__(self, surface):
        self.surface = surface
        self.font = pygame.font.SysFont("Arial", 12)

    def draw_wireframe(self, comp, text: str):
        rect = pygame.Rect(comp.x, comp.y, comp.w, comp.h)
        pygame.draw.rect(self.surface, WIREFRAME_OUTLINE_COLOUR, rect, width=1)
        pygame.draw.line(self.surface, WIREFRAME_OUTLINE_COLOUR, rect.bottomleft, rect.topright)
        text = self.font.render(text, False, WIREFRAME_TEXT_COLOUR)
        self.surface.blit(text, rect.inflate(-WIREFRAME_TEXT_PADDING, -WIREFRAME_TEXT_PADDING).topleft)

    def visit_text(self, visitor: Text):
        self.draw_wireframe(visitor, "text")

    def visit_sprite(self, visitor: Sprite):
        self.draw_wireframe(visitor, "sprite")

    def visit_video_holder(self, visitor: VideoHolder):
        self.draw_wireframe(visitor, "video")


def draw_selection_box(surface, rect):
    surf = pygame.Surface((rect.w, rect.h))
    surf.set_alpha(SELECTION_OPACITY)
    surf.fill(SELECTION_COLOUR)
    surface.blit(surf, (rect.x, rect.y))


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


class BoundingBoxRenderer:
    def __init__(self, surface):
        self.surface = surface
        self.components = []
        self.bbox = pygame.Rect(0, 0, 0, 0)

    def set_bound_components(self, components: List[Component]):
        self.components = components
        (minx, miny), (maxx, maxy) = _minmax(components)
        self.bbox = pygame.Rect(minx, miny, maxx - minx, maxy - miny)

    def draw_bounding_box(self):
        pygame.draw.rect(self.surface, BOUNDING_OUTLINE_COLOUR, self.bbox, width=1)
