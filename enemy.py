from pico2d import load_image


FRAME_W = 400
FRAME_H = 335
FRAME_COUNT = 3
DRAW_W = 220
DRAW_H = 184


class Enemy:
    def __init__(self, target_x, y):
        self.image = load_image('resources/enemy.png')
        self.x = 1380
        self.y = y
        self.target_x = target_x
        self.speed = 360
        self.frame = 0.0

    def update(self, dt):
        self.frame = (self.frame + 8.0 * dt) % FRAME_COUNT
        self.x = max(self.target_x, self.x - self.speed * dt)

    def draw(self):
        frame_idx = int(self.frame)
        self.image.clip_composite_draw(
            frame_idx * FRAME_W,
            self.image.h - FRAME_H,
            FRAME_W,
            FRAME_H,
            0,
            '',
            self.x,
            self.y,
            DRAW_W,
            DRAW_H
        )
