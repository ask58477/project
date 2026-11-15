from pico2d import clear_canvas, update_canvas, get_events, load_image
from pico2d import SDL_QUIT, SDL_KEYDOWN, SDLK_ESCAPE, SDLK_q, SDLK_e, SDLK_r
import game_framework
from player import Player
from enemy import Enemy, YellowEnemy, RedEnemy
from spawn_manager import SpawnManager

stage_timer = 0.0
game_speed = 1.0
HIT_STOP_DURATION = 0.06
hit_stop_remaining = 0.0
SCREEN_W, SCREEN_H = 1280, 720
background = None
player = None
enemies = []
spawn_manager = None

def enter():
    global stage_timer, game_speed, hit_stop_remaining, background
    global player, enemies
    global spawn_manager
    stage_timer = 0.0
    game_speed = 1.0
    hit_stop_remaining = 0.0
    background = load_image('resources/backgrounds.png')
    player = Player()
    enemies = []
    spawn_manager = SpawnManager()

def exit():
    global player, enemies
    del player
    enemies.clear()

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
            elif event.key == SDLK_q:
                enemies.append(Enemy(player.x + 80, player.y))
            elif event.key == SDLK_e:
                enemies.append(YellowEnemy(player.x + 80, player.y))
            elif event.key == SDLK_r:
                enemies.append(RedEnemy(player.x + 80, player.y))
        player.handle_event(event)

def update():
    global stage_timer, hit_stop_remaining
    if hit_stop_remaining > 0.0:
        hit_stop_remaining = max(
            0.0, hit_stop_remaining - game_framework.frame_time
        )
        return

    dt = game_framework.frame_time * game_speed
    stage_timer += dt
    player.update(dt)
    enemies.extend(spawn_manager.update(dt, player))
    slash_hitbox = player.get_slash_hitbox()
    parry_hitbox = player.get_parry_hitbox()
    player_hitbox = player.get_hitbox()
    for enemy in enemies:
        enemy.update(dt)
        if slash_hitbox is not None:
            if enemy.hit_by_slash(slash_hitbox):
                player.register_slash_hit()
        if parry_hitbox is not None:
            if enemy.hit_by_parry(parry_hitbox):
                player.register_parry_hit()
                hit_stop_remaining = max(
                    hit_stop_remaining, HIT_STOP_DURATION
                )
        if (enemy.state == 'APPROACH' and
                enemy.overlaps_hitbox(player_hitbox)):
            player.take_damage()
            enemy.knock_down()
    enemies[:] = [enemy for enemy in enemies if not enemy.is_finished]

def draw():
    clear_canvas()
    scale = max(SCREEN_W / background.w, SCREEN_H / background.h)
    background.draw(
        SCREEN_W / 2,
        SCREEN_H / 2,
        background.w * scale,
        background.h * scale
    )
    for enemy in enemies:
        enemy.draw()
    player.draw_hit_zone()
    player.draw()
    player.draw_health()
    update_canvas()
