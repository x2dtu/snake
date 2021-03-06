import pygame
import os


class Segment:
    def __init__(self, x, y, window, direction="east", width=40, vel=2, notSquare=False):
        self.x = x * width
        self.y = y * width
        if notSquare:
            self.x = x
            self.y = y
        self.width = width
        self.current_direction = direction
        self.old_direction = self.current_direction
        self.old_x, self.old_y = self.x, self.y
        self.rect = pygame.Rect(self.x, self.y, width, width)
        self.img = None
        self.window = window
        self.velocity = vel

    def update_rect(self):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.width)

    def draw(self):
        if self.img is None:
            pygame.draw.rect(self.window, (0, 130, 255), self.rect)
        else:
            self.window.blit(self.img, (self.x, self.y))

    def move_different_directions(self, prevSegment):
        if (prevSegment.current_direction == "north" or
                prevSegment.current_direction == "south") and self.x != prevSegment.x:
            if (self.current_direction == "north" or self.current_direction == "south"):
                self.old_direction = self.current_direction
                self.current_direction = prevSegment.old_direction
            sign = 1 if prevSegment.x - self.x > 0 else -1
            self.x += sign * self.velocity

        elif (prevSegment.current_direction == "east" or
                prevSegment.current_direction == "west") and self.y != prevSegment.y:
            if (self.current_direction == "east" or self.current_direction == "west"):
                self.old_direction = self.current_direction
                self.current_direction = prevSegment.old_direction
            sign = 1 if prevSegment.y - self.y > 0 else -1
            self.y += sign * self.velocity

        else:
            self.old_direction = self.current_direction
            self.current_direction = prevSegment.current_direction

    def move(self, prevSegment):
        self.update_old_x_y()
        if prevSegment.current_direction != self.current_direction:
            self.move_different_directions(prevSegment)

        if self.current_direction == prevSegment.current_direction:
            if ((self.current_direction == "east" or self.current_direction == "west") and (self.y != prevSegment.y)) or (
                    (self.current_direction == "north" or self.current_direction == "south") and (self.x != prevSegment.x)):
                self.current_direction = prevSegment.old_direction
                self.move_different_directions(prevSegment)
                return

            if self.current_direction == "east":
                self.x += self.velocity
            elif self.current_direction == "west":
                self.x -= self.velocity
            elif self.current_direction == "south":
                self.y += self.velocity
            else:
                self.y -= self.velocity

        self.update_rect()

    def update_old_x_y(self):
        sign = None
        if self.x > self.old_x:
            sign = 1
        elif self.old_x > self.x:
            sign = -1
        else:
            sign = 0
        self.old_x += self.velocity * sign

        if self.y > self.old_y:
            sign = 1
        elif self.old_y > self.y:
            sign = -1
        else:
            sign = 0
        self.old_y += self.velocity * sign
