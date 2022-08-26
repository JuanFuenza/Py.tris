import pygame
from copy import deepcopy
from random import choice, randrange

# Global settings
W, H = 10, 20
TILE = 35
GAME_RES = W * TILE, H * TILE
RES = 600, 800
FPS = 60

# Init game
pygame.init()
sc = pygame.display.set_mode(RES)
game_sc = pygame.Surface(GAME_RES)
clock = pygame.time.Clock()

# Init music
pygame.mixer.init()
pygame.mixer.music.load("music/Canter.mp3")
pygame.mixer.music.set_volume(0.8)
pygame.mixer.music.play(loops=-1)

# game grid
grid = [pygame.Rect(x * TILE, y * TILE, TILE, TILE) for x in range(W) for y in range(H)]

run = True

# Tetris figures
figures_pos = [[(-1, 0), (-2, 0), (0, 0), (1, 0)],
            [(0, -1), (-1, -1), (-1, 0), (0, 0)],
            [(-1, 0), (-1, 1), (0, 0), (0, -1)],
            [(0, 0), (-1, 0), (0, 1), (-1, -1)],
            [(0, 0), (0, -1), (0, 1), (-1, -1)],
            [(0, 0), (0, -1), (0, 1), (1, -1)],
            [(0, 0), (0, -1), (0, 1), (-1, 0)]]

# creation and storage of figures
figures = [[pygame.Rect(x + W // 2, y + 1, 1, 1) for x, y in fig_pos] for fig_pos in figures_pos]
figure_rect = pygame.Rect(0, 0, TILE - 2, TILE - 2)
# game field
field = [[0 for i in range(W)] for j in range(H)]

anim_count, anim_speed, anim_limit = 0, 60, 2000

# Backgrounds
bg = pygame.image.load('img/bg.jpg').convert()
game_bg = pygame.image.load('img/game_bg.jpg').convert()

# Figure colors
get_color = lambda : (randrange(100, 256), randrange(100, 256), randrange(100, 256))
figure, next_figure = deepcopy(choice(figures)), deepcopy(choice(figures))
color, next_color = get_color(), get_color()

# Fonts
main_font = pygame.font.Font('font/Gemini Moon.otf', 60)
font = pygame.font.Font('font/Roboto-Regular.ttf', 35)

# Titles
title_pytris = main_font.render('PY.TRIS', True, pygame.Color('grey'))
title_score = font.render('score:', True, pygame.Color('green'))
title_record = font.render('record:', True, pygame.Color('purple'))

# Scores
score, lines = 0, 0
scores = {0: 0, 1: 100, 2: 300, 3:700, 4: 1500}

# Sound Effects
score_sound = pygame.mixer.Sound("sfx/score.wav")
reset_sound = pygame.mixer.Sound("sfx/reset.wav")

# Functions
def check_borders():
    """
    Checks if the figure touches the borders when moved
    >> Return: bool
    """
    if figure[i].x < 0 or figure[i].x > W - 1:
        return False
    elif figure[i].y > H - 1 or field[figure[i].y][figure[i].x]:
        return False
    return True

def get_record():
    """
    Checks if any records exists and if not creates a file to store the best record
    >> Return: None
    """
    try:
        with open('record') as f:
            return f.readline()
    except:
        with open('record', 'w') as f:
            f.write('0')

def set_record(record, score):
    """
    Insert best record in record file
    >> Return: None
    """
    rec = max(int(record), score)
    with open('record', 'w') as f:
        f.write(str(rec))

# Init game
while run:
    record = get_record()
    dx, rotate = 0, False
    sc.blit(bg, (0, 0))
    sc.blit(game_sc, (20, 20))
    game_sc.blit(game_bg, (0, 0))

    #delay for full lines
    for i in range(lines):
        pygame.time.wait(200)

    # controls
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                dx = -1
            elif event.key == pygame.K_RIGHT:
                dx = 1
            elif event.key == pygame.K_DOWN:
                anim_limit = 200
            elif event.key == pygame.K_UP:
                rotate = True
    
    # move Y
    figure_old = deepcopy(figure)
    for i in range(4):
        figure[i].x += dx
        if not check_borders():
            figure = deepcopy(figure_old)
            break

    # move Y
    anim_count += anim_speed
    if anim_count > anim_limit:
        anim_count = 0
        figure_old = deepcopy(figure)
        for i in range(4):
            figure[i].y += 1
            if not check_borders():
                for i in range(4):
                    field[figure_old[i].y][figure_old[i].x] = color
                figure, color = next_figure, next_color
                next_figure, next_color = deepcopy(choice(figures)), get_color()
                anim_limit = 2000
                break

    # Rotate
    center = figure[0]
    figure_old = deepcopy(figure)
    if rotate:
        for i in range(4):
            x = figure[i].y - center.y
            y = figure[i].x - center.x
            figure[i].x = center.x - x
            figure[i].y = center.y + y
            if not check_borders():
                figure = deepcopy(figure_old)
                break
    
    # Check lines
    line, lines = H - 1, 0
    for row in range(H -1, -1, -1):
        count = 0
        for i in range(W):
            if field[row][i]:
                count += 1
            field[line][i] = field[row][i]
        if count < W:
            line -= 1
            
        else:
            anim_speed += 3
            lines += 1
            score_sound.set_volume(0.5)
            score_sound.play()

    # Compute score
    score += scores[lines]

    # Draw grid
    [pygame.draw.rect(game_sc, (40,40,40), i_rect, 1) for i_rect in grid]

    # Draw figure
    for i in range(4):
        figure_rect.x = figure[i].x * TILE
        figure_rect.y = figure[i].y * TILE
        pygame.draw.rect(game_sc, color, figure_rect)

    # Draw field
    for y, raw in enumerate(field):
        for x, col in enumerate(raw):
            if col:
                figure_rect.x, figure_rect.y = x * TILE, y * TILE
                pygame.draw.rect(game_sc, col, figure_rect)

    # Draw titles
    sc.blit(title_pytris, (395, 40))
    sc.blit(title_score, (440, 400))
    sc.blit(font.render(str(score), True, pygame.Color('white')), (460, 450))
    sc.blit(title_record, (440, 650))
    sc.blit(font.render(record, True, pygame.Color('gold')), (460, 700))

    # Draw next figure
    for i in range(4):
        figure_rect.x = next_figure[i].x * TILE + 310
        figure_rect.y = next_figure[i].y * TILE + 185
        pygame.draw.rect(sc, next_color, figure_rect)
    
    # Game over
    for i in range(W):
        if field[0][i]:
            set_record(record, score)
            field = [[0 for i in range(W)] for i in range(H)]
            anim_count, anim_speed, anim_limit = 0, 60, 2000
            score = 0
            reset_sound.set_volume(0.2)
            reset_sound.play()
            for i_rect in grid:
                pygame.draw.rect(game_sc, get_color(), i_rect)
                sc.blit(game_sc, (20,20))
                pygame.display.flip()
                clock.tick(200)


    pygame.display.flip()
    clock.tick(FPS)