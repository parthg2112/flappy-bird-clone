import pygame, random, time, sys

def draw_floor():
    screen.blit(floor_surface, (floor_x_pos, 450))
    screen.blit(floor_surface, (floor_x_pos + 288, 450))

def create_pipe():
    random_pipe_pos = random.choice(pipe_height)
    bottom_pipe = pipe_surface.get_rect(midtop = (700, random_pipe_pos))
    top_pipe = pipe_surface.get_rect(midbottom = (700, random_pipe_pos - 120))
    return bottom_pipe, top_pipe

def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= 2
    visible_pipes = [pipe for pipe in pipes if pipe.centerx > -50]  # Remove off-screen pipes
    return visible_pipes

def draw_pipes(pipes):
    for pipe in pipes:
        if pipe.bottom >= 512:
            screen.blit(pipe_surface, pipe)
        else:
            flip_pipe = pygame.transform.flip(pipe_surface, False, True)
            screen.blit(flip_pipe, pipe)

def check_collision(pipes):
    for pipe in pipes:
       if bird_rect.colliderect(pipe):
           death_sound.play()
           return False
    if bird_rect.top <= -100 or bird_rect.bottom >= 450:
        death_sound.play()
        return False
    return True

def rotate_bird(bird):
    new_bird = pygame.transform.rotozoom(bird, -bird_movement*2, 1)
    return new_bird

def bird_animation():
    new_bird = bird_frames[bird_index]
    new_bird_rect = new_bird.get_rect(center = (50, bird_rect.centery))
    return new_bird, new_bird_rect

def score_display(game_state):
    if game_state == "main_game":
        score_surface = gameFont.render(str(int(score)), True, (255,255,255))
        score_rect = score_surface.get_rect(center=(144, 50))
        screen.blit(score_surface, score_rect)
    if game_state == "game_over":
        score_surface = gameFont.render(f'Score: {int(score)}', True, (255,255,255))
        score_rect = score_surface.get_rect(center=(144, 200))
        screen.blit(score_surface, score_rect)

        high_score_surface = gameFont.render(f'High Score: {int(high_score)}', True, (255,255,255))
        high_score_rect = high_score_surface.get_rect(center=(144, 410))
        screen.blit(high_score_surface, high_score_rect)

def update_score(score, high_score):
    if score > high_score:
        high_score = score
    return high_score

def pipe_score_check():
    global score, can_score

    if pipe_list:
        for pipe in pipe_list:
            # Check if bird passed through the gap between pipes (only check bottom pipes)
            if pipe.bottom >= 512 and 47 < pipe.centerx < 53 and can_score:
                score += 1
                score_sound.play()
                can_score = False
            elif pipe.centerx < 40:  # Reset scoring when pipe is well past the bird
                can_score = True

def save_high_score():
    try:
        with open('high_score.txt', 'w') as f:
            f.write(str(int(high_score)))
    except:
        pass  # If file operations fail, just continue

def load_high_score():
    try:
        with open('high_score.txt', 'r') as f:
            return int(f.read().strip())
    except:
        return 0  # Return 0 if file doesn't exist or can't be read

pygame.mixer.pre_init(frequency=44100, size=16, channels=1, buffer=512)
pygame.init()

# screen
screen_width = 288
screen_height = 512
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

gameFont = pygame.font.Font('04B_19__.TTF',30)

# game variables
gravity = 0.1
bird_movement = 0
game_active = True

score = 0
high_score = load_high_score()  # Load high score from file
can_score = True

bg_surface = pygame.image.load('sprites/background-day.png').convert_alpha()
floor_surface = pygame.image.load('sprites/base.png').convert_alpha()
floor_x_pos = 0

bird_downflap = pygame.image.load('sprites/bluebird-downflap.png').convert_alpha()
bird_midflap = pygame.image.load('sprites/bluebird-midflap.png').convert_alpha()
bird_upflap = pygame.image.load('sprites/bluebird-upflap.png').convert_alpha()
bird_frames = [bird_downflap, bird_midflap, bird_upflap]
bird_index = 0
bird_surface = bird_frames[bird_index]
bird_rect = bird_surface.get_rect(center = (50,256))

BIRDFLAP = pygame.USEREVENT+1
pygame.time.set_timer(BIRDFLAP, 100)

pipe_surface = pygame.image.load('sprites/pipe-green.png').convert_alpha()
pipe_list =[]
SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, 1200)
pipe_height = [200,225,250,275,300,325,350,360]

game_over_surface = pygame.image.load('sprites/message.png').convert_alpha()
game_over_rect = game_over_surface.get_rect(center=(144, 256))

flap_sound = pygame.mixer.Sound('sound/sfx_wing.wav')
death_sound = pygame.mixer.Sound('sound/sfx_hit.wav')
score_sound = pygame.mixer.Sound('sound/sfx_point.wav')

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_high_score()  # Save high score before quitting
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_active:
                bird_movement = 0
                bird_movement -= 3
                flap_sound.play()

            if game_active == False and event.key == pygame.K_SPACE:
                game_active = True
                pipe_list.clear()
                bird_rect.center = (50,256)
                bird_movement = 0
                score = 0
                can_score = True

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT and game_active:
                bird_movement = 0
                bird_movement -= 3
                flap_sound.play()

            if game_active == False and event.button == pygame.BUTTON_LEFT:
                game_active = True
                pipe_list.clear()
                bird_rect.center = (50,256)
                bird_movement = 0
                score = 0
                can_score = True

        if event.type == SPAWNPIPE:
            pipe_list.extend(create_pipe())

        if event.type == BIRDFLAP:
            if bird_index < 2:
                bird_index += 1
            else:
                bird_index = 0

            bird_surface, bird_rect = bird_animation()

    screen.blit(bg_surface, (0,0))

    if game_active:
        # bird
        bird_movement += gravity
        rotated_bird = rotate_bird(bird_surface)
        bird_rect.centery += bird_movement
        screen.blit(rotated_bird, bird_rect)
        game_active = check_collision(pipe_list)

        # pipes
        pipe_list = move_pipes(pipe_list)
        draw_pipes(pipe_list)

        pipe_score_check()
        score_display('main_game')
    else:
        screen.blit(game_over_surface, game_over_rect)
        high_score = update_score(score, high_score)
        score_display('game_over')

    # floor
    floor_x_pos -= 1
    draw_floor()
    if floor_x_pos <= -288:
        floor_x_pos = 0

    pygame.display.update()
    clock.tick(120)