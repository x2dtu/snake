import pygame
import os
import sys

from head import Head
from tail import Tail
from segment import Segment
from apple import Apple

pygame.init()

WINDOW = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
pygame.display.set_caption("Snake Game")

BG = pygame.image.load(os.path.join('assets', 'snake_background.jpg'))
BG_SQUARE_WIDTH = 40

EAT_APPLE_SOUND = pygame.mixer.Sound(os.path.join('assets', 'eat_apple.mp3'))
LOST_SOUND = pygame.mixer.Sound(os.path.join('assets', 'lost.mp3'))
GAME_START_SOUND = pygame.mixer.Sound(os.path.join('assets', 'game_start.mp3'))
MOVE_SOUND = pygame.mixer.Sound(os.path.join('assets', 'move.mp3'))

FPS = 100
clock = pygame.time.Clock()

segments = []
has_lost = False
# mouse pointer coordinates (set to a tuple (x, y) whenever the game is lost)
mouse = None


def init():
    global has_lost, segments
    middle_x_space = (WINDOW.get_width() // BG_SQUARE_WIDTH) // 2
    middle_y_space = (WINDOW.get_height() // BG_SQUARE_WIDTH) // 2

    segments = [Head(middle_x_space, middle_y_space, WINDOW, width=BG_SQUARE_WIDTH),
                Segment(middle_x_space - 1, middle_y_space,
                        WINDOW, width=BG_SQUARE_WIDTH),
                Segment(middle_x_space - 2, middle_y_space,
                        WINDOW, width=BG_SQUARE_WIDTH),
                Segment(middle_x_space - 3, middle_y_space,
                        WINDOW, width=BG_SQUARE_WIDTH),
                Tail(middle_x_space - 4, middle_y_space, WINDOW, width=BG_SQUARE_WIDTH)]

    has_lost = False
    GAME_START_SOUND.play()


init()
apples = [Apple(WINDOW, segments)]

# Cache for speed
_circle_cache = {}


def _circlepoints(r):
    # creates outline of r pixels around text
    r = int(round(r))
    if r in _circle_cache:
        return _circle_cache[r]
    x, y, e = r, 0, 1 - r
    _circle_cache[r] = points = []
    while x >= y:
        points.append((x, y))
        y += 1
        if e < 0:
            e += 2 * y - 1
        else:
            x -= 1
            e += 2 * (y - x) - 1
    points += [(y, x) for x, y in points if x > y]
    points += [(-x, y) for x, y in points if x]
    points += [(x, -y) for x, y in points if y]
    points.sort()
    return points


def render_text(text, font_type, size, textcolor=(255, 255, 255), outlinecolor=(0, 0, 0), outlinepx=2):
    font = pygame.font.SysFont(font_type, size)
    textsurface = font.render(text, True, textcolor).convert_alpha()
    width = textsurface.get_width() + 2 * outlinepx
    height = font.get_height()

    outline_surf = pygame.Surface(
        (width, height + 2 * outlinepx)).convert_alpha()
    outline_surf.fill((0, 0, 0, 0))

    surf = outline_surf.copy()

    outline_surf.blit(font.render(
        text, True, outlinecolor).convert_alpha(), (0, 0))

    for dx, dy in _circlepoints(outlinepx):
        surf.blit(outline_surf, (dx + outlinepx, dy + outlinepx))

    surf.blit(textsurface, (outlinepx, outlinepx))
    return surf


def ate_apple():
    EAT_APPLE_SOUND.play()
    delta_x = segments[-1].x - segments[-2].x
    delta_y = segments[-1].y - segments[-2].y
    # segments will grow by one, and the last segment will be delta_x and delta_y away from the previous last
    segments.insert(-1, Segment(segments[-1].x, segments[-1].y,
                                WINDOW, width=BG_SQUARE_WIDTH, notSquare=True, direction=segments[-1].current_direction))
    segments[-2].old_direction = segments[-1].old_direction
    segments[-1].x, segments[-1].y = segments[-1].x + \
        delta_x, segments[-1].y + delta_y
    apples[0] = Apple(WINDOW, segments)


def check_collision():
    """Returns False if we lost (hit edge of screen or our own body), else returns True"""
    if (segments[0].x < 0 or segments[0].x > WINDOW.get_width() - segments[0].width) or (
            segments[0].y < 0 or segments[0].y > WINDOW.get_height() - segments[0].width):
        # then we are off screen
        return False

    # next we check if our head has collided with our body
    # we get the segments starting from the third segment as the head (the first segment)
    # will collide with second segment whenever we turn
    rect_segments = segments[2:-1]
    rect_segments.append(segments[-1].rect)

    if any([segments[0].rect.colliderect(rect_segment) for rect_segment in rect_segments]):
        # then we hit our body
        return False

    if segments[0].rect.colliderect(apples[0].img.get_rect(topleft=(apples[0].x, apples[0].y))):
        ate_apple()
    return True


def mouse_over_button(dimensions):
    # precondtion: mouse is not None
    # expects a single param that is a tuple of 4 ints: x pos, y pos, width, and height of button
    x, y, width, height = dimensions
    return (mouse[0] >= x and mouse[0] <= x + width) and (
        mouse[1] >= y and mouse[1] <= y + height)


def lose():
    global has_lost
    if not has_lost:
        LOST_SOUND.play()
        has_lost = True

    width, height = WINDOW.get_width(), WINDOW.get_height()

    dark = pygame.Surface((width, height))
    dark.set_alpha(180)
    dark.fill((0, 0, 0))
    WINDOW.blit(dark, (0, 0))

    white_rect_width, white_rect_height = width // 2, height // 2
    white_rect_pos_x, white_rect_pos_y = (
        width - white_rect_width) // 2, (height - white_rect_height) // 2
    pygame.draw.rect(WINDOW, (230, 230, 230), (white_rect_pos_x,
                     white_rect_pos_y, white_rect_width, white_rect_height), border_radius=10)

    you_lost_text = render_text("You Lost!", 'consolas', 40)
    you_lost_y_pos = white_rect_pos_y + 20
    WINDOW.blit(you_lost_text, (white_rect_pos_x + (white_rect_width -
                you_lost_text.get_width()) // 2, you_lost_y_pos))

    apples_eaten_text = render_text(
        f"You ate {len(segments) - 5} apples", 'consolas', 25)
    apples_eaten_y_pos = you_lost_y_pos + you_lost_text.get_height() + 20
    WINDOW.blit(apples_eaten_text, (white_rect_pos_x + (white_rect_width -
                apples_eaten_text.get_width()) // 2, apples_eaten_y_pos))

    apples_eaten_text_disp = apples_eaten_y_pos + apples_eaten_text.get_height()
    play_again_button_width, play_again_button_height = white_rect_width // 2, (
        white_rect_pos_y + white_rect_height - apples_eaten_y_pos) // 2
    play_again_button_x_pos, play_again_button_y_pos = (white_rect_width + play_again_button_width) // 2, apples_eaten_text_disp + \
        (white_rect_pos_y + white_rect_height - apples_eaten_text_disp) // 2 - \
        play_again_button_height // 2

    color = (60, 100, 230)
    if mouse is not None and mouse_over_button((play_again_button_x_pos, play_again_button_y_pos,
                                               play_again_button_width, play_again_button_height)):
        color = (70, 70, 70)
    pygame.draw.rect(WINDOW, color, (play_again_button_x_pos, play_again_button_y_pos,
                     play_again_button_width, play_again_button_height), border_radius=10)

    play_again_text = render_text("Play Again", 'consolas', 25)
    play_again_text_x_pos = play_again_button_x_pos + \
        (play_again_button_width - play_again_text.get_width()) // 2
    play_again_text_y_pos = play_again_button_y_pos + \
        (play_again_button_height - play_again_text.get_height()) // 2
    WINDOW.blit(play_again_text,
                (play_again_text_x_pos, play_again_text_y_pos))

    # return the x, y, width, and height of play button -> these will be needed later so that we know if we clicked it
    return (play_again_button_x_pos, play_again_button_y_pos, play_again_button_width, play_again_button_height)


def draw_screen():
    WINDOW.blit(BG, (0, 0))
    for apple in apples:
        apple.draw()
    for segment in segments[::-1]:
        segment.draw()
    text = render_text(f'Score: {len(segments) - 5}', 'consolas', 25)
    WINDOW.blit(text, (7, 7))


def tick():
    clock.tick(FPS)
    if not check_collision() or has_lost:
        draw_screen()
        lose()
    else:
        for i in range(len(segments)):
            segments[i].move(segments[i-1])
        draw_screen()
    pygame.display.update()


def loop_music():
    pygame.mixer.music.play(-1)


while True:
    if has_lost:
        mouse = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()

        if has_lost and event.type == pygame.MOUSEBUTTONDOWN:
            if (mouse_over_button(lose())):
                init()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w or event.key == pygame.K_i:
                if segments[0].change_direction("north"):
                    MOVE_SOUND.play()
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s or event.key == pygame.K_k:
                if segments[0].change_direction("south"):
                    MOVE_SOUND.play()
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d or event.key == pygame.K_l:
                if segments[0].change_direction("east"):
                    MOVE_SOUND.play()
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a or event.key == pygame.K_j:
                if segments[0].change_direction("west"):
                    MOVE_SOUND.play()

    if not has_lost and segments[0].previous_direction != segments[0].current_direction:
        # save current_direction
        new_direction = segments[0].current_direction
        segments[0].current_direction = segments[0].previous_direction

        x_ratio, y_ratio = round(
            segments[0].x / BG_SQUARE_WIDTH), round(segments[0].y / BG_SQUARE_WIDTH)
        x_ratio_dif = segments[0].x - x_ratio * BG_SQUARE_WIDTH
        y_ratio_dif = segments[0].y - y_ratio * BG_SQUARE_WIDTH

        while ((segments[0].pixels_traveled_since_direction_change < BG_SQUARE_WIDTH
                ) or (segments[0].x % BG_SQUARE_WIDTH != 0 or segments[0].y % BG_SQUARE_WIDTH != 0)):
            tick()

        segments[0].current_direction = new_direction
        segments[0].previous_direction = new_direction
        segments[0].pixels_traveled_since_direction_change = 0
    else:
        tick()
