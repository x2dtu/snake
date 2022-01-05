import pygame
import os
from segment import Segment


class Head(Segment):
    def __init__(self, x, y, window, width=40, direction="east"):
        super().__init__(x, y, window, width=width, direction=direction)
        self.original_img = pygame.transform.rotate(pygame.image.load(
            os.path.join('assets', 'snake_head.png')), 0)
        self.img = pygame.transform.rotate(self.original_img, -90)
        self.previous_direction = self.current_direction
        self.pixels_traveled_since_direction_change = 0

    # override parent move
    def move(self, _):
        # in this case, second arg is the tail
        # we don't care about prevSegment (second arg)
        self.update_old_x_y()
        if self.current_direction == "north":
            self.y -= self.velocity
            self.img = pygame.transform.rotate(self.original_img, 0)
        elif self.current_direction == "south":
            self.y += self.velocity
            self.img = pygame.transform.rotate(self.original_img, 180)
        elif self.current_direction == "east":
            self.x += self.velocity
            self.img = pygame.transform.rotate(self.original_img, -90)
        else:  # west
            self.x -= self.velocity
            self.img = pygame.transform.rotate(self.original_img, 90)
        self.update_rect()
        self.pixels_traveled_since_direction_change += self.velocity

    def change_direction(self, new_direction):
        if (new_direction == self.current_direction):
            return False
        if (self.current_direction == "east" and new_direction == "west") or (
                self.current_direction == "west" and new_direction == "east") or (
                self.current_direction == "north" and new_direction == "south") or (
                self.current_direction == "south" and new_direction == "north"):
            return False
        self.old_direction = self.current_direction
        self.current_direction = new_direction
        return True
