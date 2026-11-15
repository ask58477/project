from pico2d import clear_canvas, update_canvas, get_events
from pico2d import SDL_QUIT, SDL_KEYDOWN, SDLK_ESCAPE, SDLK_q, SDLK_e
import game_framework
from player import Player
from enemy import Enemy, YellowEnemy

stage_timer = 0.0
game_speed = 1.0
player = None
enemies = []

def enter():
    global stage_timer, game_speed, player, enemies
    stage_timer = 0.0
    game_speed = 1.0
    player = Player()
    enemies = []

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
        player.handle_event(event)

def update():
    global stage_timer
    dt = game_framework.frame_time * game_speed
    stage_timer += dt
    player.update(dt)
    slash_hitbox = player.get_slash_hitbox()
    parry_hitbox = player.get_parry_hitbox()
    player_hitbox = player.get_hitbox()
    for enemy in enemies:
        enemy.update(dt)
        if slash_hitbox is not None:
            enemy.hit_by_slash(slash_hitbox)
        if parry_hitbox is not None:
            enemy.hit_by_parry(parry_hitbox)
        if (enemy.state == 'APPROACH' and
                enemy.overlaps_hitbox(player_hitbox)):
            player.take_damage()
            enemy.knock_down()
    enemies[:] = [enemy for enemy in enemies if not enemy.is_finished]

def draw():
    clear_canvas()
    for enemy in enemies:
        enemy.draw()
    player.draw_hit_zone()
    player.draw()
    player.draw_health()
    update_canvas()
