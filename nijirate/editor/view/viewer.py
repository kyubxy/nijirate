from typing import List

import pygame

from editor.model.component import VideoHolder
from editor.model.state import State, StateObserver
from editor.view.base import Base
from editor.view.renderer import Renderer


class Viewer(Base, StateObserver):

    def __init__(self, state: State, detached: bool = False):
        super().__init__()
        pygame.display.set_caption("Editor [DETACHED]" if detached else "Editor")

        self.font = pygame.font.SysFont("Arial", 12)
        self.renderer = Renderer(self.screen)
        self.state = state

    def onmessage(self, msg: (str, List[any])):
        pass

    def update(self, events):
        for event in events:
            ...

    def draw(self):
        self.screen.fill((0, 0, 0))
        for c in self.state.scenegraph:
            c.accept(self.renderer)
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
