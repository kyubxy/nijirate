from abc import abstractmethod, ABC
from typing import List

import pygame

from editor.model.state import State


class MouseController:
    def __init__(self, state: State):
        self.state = state

    def update(self, events):
        mx, my = pygame.mouse.get_pos()
        for event in events:
            if event == pygame.MOUSEBUTTONDOWN:
                pass
            if event == pygame.MOUSEBUTTONUP:
                pass
