import random
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
SLASH_SHAKE_STRENGTH = 3
SLASH_SHAKE_DURATION = 0.1
PARRY_SHAKE_STRENGTH = 6
PARRY_SHAKE_DURATION = 0.16
DAMAGE_SHAKE_STRENGTH = 10
DAMAGE_SHAKE_DURATION = 0.24
EFFECT_FRAME_COUNT = 6
EFFECT_FRAME_DURATION = 0.04
EFFECT_FRAME_WIDTH = 320
EFFECT_FRAME_STRIDE = 300
EFFECT_FRAME_HEIGHT = 400
EFFECT_FRAME_TOP = 300
EFFECT_DRAW_W = 192
EFFECT_DRAW_H = 240
camera_shake_remaining = 0.0
camera_shake_duration = 0.0
camera_shake_strength = 0.0
camera_offset_x = 0.0
camera_offset_y = 0.0
SCREEN_W, SCREEN_H = 1280, 720
background = None
parry_effect_image = None
parry_effects = []
player = None
enemies = []
spawn_manager = None

class ParryEffect:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.elapsed = 0.0

    def update(self, dt):
        self.elapsed += dt

    @property
    def is_finished(self):
        return self.elapsed >= EFFECT_FRAME_COUNT * EFFECT_FRAME_DURATION

    def draw(self, cam_x, cam_y):
        frame = min(
            int(self.elapsed / EFFECT_FRAME_DURATION),
            EFFECT_FRAME_COUNT - 1
        )
        parry_effect_image.clip_composite_draw(
            frame * EFFECT_FRAME_STRIDE,
            parry_effect_image.h - EFFECT_FRAME_TOP - EFFECT_FRAME_HEIGHT,
            EFFECT_FRAME_WIDTH,
            EFFECT_FRAME_HEIGHT,
            0,
            '',
            self.x + cam_x,
            self.y + cam_y,
            EFFECT_DRAW_W,
            EFFECT_DRAW_H
        )

def enter():
    global stage_timer, game_speed, hit_stop_remaining, background
    global camera_shake_remaining, camera_shake_duration
    global camera_shake_strength, camera_offset_x, camera_offset_y
    global parry_effect_image, parry_effects, player, enemies
    global spawn_manager
    stage_timer = 0.0
    game_speed = 1.0
    hit_stop_remaining = 0.0
    camera_shake_remaining = 0.0
    camera_shake_duration = 0.0
    camera_shake_strength = 0.0
    camera_offset_x = 0.0
    camera_offset_y = 0.0
    background = load_image('resources/backgrounds.png')
    parry_effect_image = load_image('resources/effect.png')
    parry_effects = []
    player = Player()
    enemies = []
    spawn_manager = SpawnManager()

def exit():
    global player, enemies, parry_effects
    del player
    enemies.clear()
    parry_effects.clear()

def pause():
    pass

def resume():
    pass

def trigger_camera_shake(strength, duration):
    global camera_shake_remaining, camera_shake_duration
    global camera_shake_strength
    camera_shake_strength = max(camera_shake_strength, strength)
    camera_shake_duration = max(camera_shake_duration, duration)
    camera_shake_remaining = max(camera_shake_remaining, duration)

def update_camera_shake(dt):
    global camera_shake_remaining, camera_shake_duration
    global camera_shake_strength, camera_offset_x, camera_offset_y
    if camera_shake_remaining <= 0.0:
        camera_offset_x = 0.0
        camera_offset_y = 0.0
        return

    camera_shake_remaining = max(0.0, camera_shake_remaining - dt)
    if camera_shake_remaining == 0.0:
        camera_shake_duration = 0.0
        camera_shake_strength = 0.0
        camera_offset_x = 0.0
        camera_offset_y = 0.0
        return

    intensity = (
        camera_shake_strength *
        camera_shake_remaining / camera_shake_duration
    )
    camera_offset_x = random.uniform(-intensity, intensity)
    camera_offset_y = random.uniform(-intensity, intensity)

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
    update_camera_shake(game_framework.frame_time)
    if hit_stop_remaining > 0.0:
        hit_stop_remaining = max(
            0.0, hit_stop_remaining - game_framework.frame_time
        )
        return

    dt = game_framework.frame_time * game_speed
    stage_timer += dt
    player.update(dt)
    for effect in parry_effects:
        effect.update(dt)
    parry_effects[:] = [
        effect for effect in parry_effects if not effect.is_finished
    ]
    enemies.extend(spawn_manager.update(dt, player))
    slash_hitbox = player.get_slash_hitbox()
    parry_hitbox = player.get_parry_hitbox()
    player_hitbox = player.get_hitbox()
    for enemy in enemies:
        enemy.update(dt)
        if slash_hitbox is not None:
            if enemy.hit_by_slash(slash_hitbox):
                player.register_slash_hit()
                trigger_camera_shake(
                    SLASH_SHAKE_STRENGTH, SLASH_SHAKE_DURATION
                )
        if parry_hitbox is not None:
            if enemy.hit_by_parry(parry_hitbox):
                player.register_parry_hit()
                hit_stop_remaining = max(
                    hit_stop_remaining, HIT_STOP_DURATION
                )
                trigger_camera_shake(
                    PARRY_SHAKE_STRENGTH, PARRY_SHAKE_DURATION
                )
                parry_effects.append(ParryEffect(enemy.x, enemy.y))
        if (enemy.state == 'APPROACH' and
                enemy.overlaps_hitbox(player_hitbox)):
            if player.take_damage():
                trigger_camera_shake(
                    DAMAGE_SHAKE_STRENGTH, DAMAGE_SHAKE_DURATION
                )
            enemy.knock_down()
    enemies[:] = [enemy for enemy in enemies if not enemy.is_finished]

def draw():
    clear_canvas()
    scale = max(SCREEN_W / background.w, SCREEN_H / background.h)
    background.draw(
        SCREEN_W / 2 + camera_offset_x,
        SCREEN_H / 2 + camera_offset_y,
        background.w * scale,
        background.h * scale
    )
    for enemy in enemies:
        enemy.draw(camera_offset_x, camera_offset_y)
    player.draw_hit_zone(camera_offset_x, camera_offset_y)
    player.draw(camera_offset_x, camera_offset_y)
    for effect in parry_effects:
        effect.draw(camera_offset_x, camera_offset_y)
    player.draw_health(camera_offset_x, camera_offset_y)
    update_canvas()
