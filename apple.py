import pygame
import os
import random


class Apple:
    def __init__(self, window, segments):
        self.window = window
        self.segments = segments
        self.width = segments[0].width
        self.img = pygame.image.load(os.path.join('assets', 'apple.png'))

        def calculate_available_spaces():
            available_spaces = []
            rows = range(
                window.get_height() // self.width)
            columns = range(
                window.get_width() // self.width)
            taken_spaces = {(segment.x // self.width, segment.y //
                             self.width) for segment in segments}
            for row in rows:
                for col in columns:
                    if (col, row) not in taken_spaces:
                        available_spaces.append(
                            (col * self.width, row * self.width))
            return available_spaces

        def random_posisition(available_spaces):
            rand_index = random.randrange(len(available_spaces))
            if len(available_spaces) > 0:
                return available_spaces[rand_index]
            # if we can't find a spot for the apple, spawn it off screen
            return -self.width, -self.width

        self.x, self.y = random_posisition(calculate_available_spaces())

    def draw(self):
        self.window.blit(self.img, (self.x, self.y))
