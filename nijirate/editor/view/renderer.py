import pygame

from editor.model.component import ComponentVisitor, Text, VideoHolder, Sprite

class Renderer(ComponentVisitor):
    def __init__(self, surface):
        self.surface = surface
        self.font = pygame.font.SysFont("Arial", 12)

    def draw_wireframe(self, comp, text: str):
        rect = pygame.Rect(comp.x, comp.y, comp.w, comp.h)
        pygame.draw.rect(self.surface, (255, 255, 255), rect, width=1)
        pygame.draw.line(self.surface, (255, 255, 255), rect.bottomleft, rect.topright)
        self.surface.blit(self.font.render(text, False, (100, 100, 100)), rect.inflate(-10, -10).topleft)

    def visit_text(self, visitor: Text):
        self.draw_wireframe(visitor, "text")

    def visit_sprite(self, visitor: Sprite):
        self.draw_wireframe(visitor, "sprite")

    def visit_video_holder(self, visitor: VideoHolder):
        self.draw_wireframe(visitor, "video")

