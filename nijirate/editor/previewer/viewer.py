from typing import List

import pygame

from editor.component import VideoHolder, Text
from editor.previewer.control import MouseSelector
from editor.state import State, StateObserver
from editor.previewer.base import Base
from editor.previewer.renderer import ComponentRenderer, GizmoRenderer, draw_selection_box


class Viewer(Base, StateObserver):

    def __init__(self, state: State, detached: bool = False):
        super().__init__()
        pygame.display.set_caption("Editor [DETACHED]" if detached else "Editor")

        self.state = state
        self.state.attach_observer(self)

        self.crenderer = ComponentRenderer(self.screen)
        self.grenderer = GizmoRenderer(self.screen)
        self.controller = MouseSelector(self.state)

        self.font = pygame.font.SysFont("Arial", 12)

    def onmessage(self, message: (str, List[any])):
        pass

    def update(self, events):
        for event in events:
            pos = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.controller.mousedown(pos)
            if event.type == pygame.MOUSEBUTTONUP:
                self.controller.domouseup(pos)
            if event.type == pygame.MOUSEMOTION:
                self.controller.mousemotion(pos)

    def draw_gizmos(self):
        # we'll excuse the selection box from the gizmo ecosystem for the time being
        sbox = self.state.get_selection_box()
        if sbox.w * sbox.h > 0:
            draw_selection_box(self.screen, sbox)
        bb = self.state.get_boundingbox()
        if bb is not None:
            bb.accept(self.grenderer)

    def draw_scenegraph(self):
        for c in self.state.get_scenegraph():
            c.accept(self.crenderer)

    def draw(self):
        self.screen.fill((0, 0, 0))

        self.draw_scenegraph()
        self.draw_gizmos()

        self.screen.blit(self.font.render("The editor is currently DETACHED. No communication is being made with "
                                          "other parts of the program", False, (255, 0, 0)), (0, 0))
        pygame.display.flip()


if __name__ == "__main__":
    s = State()
    vh = VideoHolder()
    vh.x = 60
    vh.y = 40
    vh.w = 300
    vh.h = 200
    text = Text()
    text.x = 500
    text.y = 300
    text.w = 40
    text.h = 40
    s.get_scenegraph().append(vh)
    s.get_scenegraph().append(text)
    e = Viewer(s, True)
    e.run()
