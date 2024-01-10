from typing import List

import pygame

from editor.control.mousecontroller import MouseController
from editor.model.component import VideoHolder
from editor.model.state import State, StateObserver
from editor.view.base import Base
from editor.view.renderer import ComponentRenderer, BoundingBoxRenderer, draw_selection_box


class Viewer(Base, StateObserver):

    def __init__(self, state: State, detached: bool = False):
        super().__init__()
        pygame.display.set_caption("Editor [DETACHED]" if detached else "Editor")

        self.state = state
        self.state.attach_observer(self)

        self.crenderer = ComponentRenderer(self.screen)
        self.bbrenderer = BoundingBoxRenderer(self.screen, state)
        self.mousecontroller = MouseController(self.state)

        self.font = pygame.font.SysFont("Arial", 12)

    def onmessage(self, message: (str, List[any])):
        pass

    def update(self, events):
        self.mousecontroller.update(events)

    def draw_gizmos(self):
        sbox = self.state.get_selected_box()
        if sbox.w * sbox.h > 0:
            draw_selection_box(self.screen, sbox)
        self.bbrenderer.draw_bounding_box()

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
    s.get_scenegraph().append(vh)
    e = Viewer(s, True)
    e.run()
