import pygame

from editor.model.component import ComponentVisitor, Text, VideoHolder, Sprite

WIREFRAME_OUTLINE_COLOUR = (255, 255, 255)
WIREFRAME_TEXT_COLOUR = (100, 100, 100)
WIREFRAME_TEXT_PADDING = 10

SELECTION_COLOUR = (0, 100, 255)
SELECTION_OPACITY = 128


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


class GizmoRenderer:
    def __init__(self, surface):
        self.surface = surface

    def draw_selection_box(self, rect):
        surf = pygame.Surface((rect.w, rect.h))
        surf.set_alpha(SELECTION_OPACITY)
        surf.fill(SELECTION_COLOUR)
        self.surface.blit(surf, (rect.x, rect.y))
