from typing import List

import pygame

from editor.control.mouselistener import MouseListener
from editor.control.selector import Selector
from editor.model.state import State


class MouseController:
    def __init__(self, state: State):
        self.layeredinputpool: List[MouseListener] = [
            Selector(state)
        ]

    def update(self, events):
        for event in events:
            pos = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for ml in self.layeredinputpool:
                    ml.mousedown(pos)
            if event.type == pygame.MOUSEBUTTONUP:
                for ml in self.layeredinputpool:
                    ml.domouseup(pos)
            if event.type == pygame.MOUSEMOTION:
                for ml in self.layeredinputpool:
                    ml.mousemotion(pos)
