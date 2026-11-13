from pico2d import clear_canvas, update_canvas, get_events
from pico2d import SDL_QUIT, SDL_KEYDOWN, SDLK_ESCAPE
import game_framework
from player import Player

stage_timer = 0.0
game_speed = 1.0
player = None

def enter():
    global stage_timer, game_speed, player
    stage_timer = 0.0
    game_speed = 1.0
    player = Player()

def exit():
    global player
    del player

def pause():
    pass

def resume():
    pass

def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.quit()
        player.handle_event(event)

def update():
    global stage_timer
    dt = game_framework.frame_time * game_speed
    stage_timer += dt
    player.update(dt)

def draw():
    clear_canvas()
    player.draw_hit_zone()
    player.draw()
    update_canvas()