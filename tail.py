import pygame
import os

from segment import Segment


class Tail(Segment):
    def __init__(self, x, y, window, width=40, direction="east"):
        super().__init__(x, y, window, direction=direction, width=width)
        self.original_img = pygame.image.load(
            os.path.join('assets', 'snake_tail.png'))
        self.img = pygame.transform.rotate(self.original_img, 90)

    def move(self, prevSegment):
        if self.current_direction == "east":
            self.img = pygame.transform.rotate(self.original_img, 90)
        elif self.current_direction == "west":
            self.img = pygame.transform.rotate(self.original_img, -90)
        elif self.current_direction == "south":
            self.img = pygame.transform.rotate(self.original_img, 0)
        else:  # going up
            self.img = pygame.transform.rotate(self.original_img, 180)

        super().move(prevSegment)
