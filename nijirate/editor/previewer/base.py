from abc import ABC

import pygame

WIDTH = 16 * 60
HEIGHT = 9 * 60
FPS = 160


class Base(ABC):
    def __init__(self):
        pygame.init()
        pygame.font.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

    def update(self, events):
        pass

    def draw(self):
        pass

    def run(self):
        running = True
        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
            self.update(events)
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
