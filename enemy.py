from pico2d import load_image


FRAME_W = 400
FRAME_H = 335
FRAME_COUNT = 3
KNOCKDOWN_FRAMES = (4, 3, 5)
KNOCKDOWN_FRAME_DURATION = 0.12
DRAW_W = 220
DRAW_H = 184
HITBOX_HALF_W = 40
HITBOX_HALF_H = 55


class Enemy:
    def __init__(self, target_x, y):
        self.image = load_image('resources/enemy.png')
        self.x = 1380
        self.y = y
        self.target_x = target_x
        self.speed = 360
        self.frame = 0.0
        self.state = 'APPROACH'
        self.knockdown_elapsed = 0.0

    def update(self, dt):
        if self.state == 'KNOCKED_DOWN':
            self.knockdown_elapsed = min(
                self.knockdown_elapsed + dt,
                len(KNOCKDOWN_FRAMES) * KNOCKDOWN_FRAME_DURATION
            )
            return
        if self.state != 'APPROACH':
            return

        self.frame = (self.frame + 8.0 * dt) % FRAME_COUNT
        self.x = max(self.target_x, self.x - self.speed * dt)

    @property
    def is_finished(self):
        return (
            self.state == 'KNOCKED_DOWN' and
            self.knockdown_elapsed >=
            len(KNOCKDOWN_FRAMES) * KNOCKDOWN_FRAME_DURATION
        )

    def hit_by_slash(self, hitbox):
        if self.state != 'APPROACH':
            return False

        left, bottom, right, top = hitbox
        enemy_left = self.x - HITBOX_HALF_W
        enemy_right = self.x + HITBOX_HALF_W
        enemy_bottom = self.y - HITBOX_HALF_H
        enemy_top = self.y + HITBOX_HALF_H
        if (enemy_left > right or enemy_right < left or
                enemy_bottom > top or enemy_top < bottom):
            return False

        self.state = 'KNOCKED_DOWN'
        self.knockdown_elapsed = 0.0
        return True

    def draw(self):
        if self.state == 'KNOCKED_DOWN':
            knockdown_idx = min(
                int(self.knockdown_elapsed / KNOCKDOWN_FRAME_DURATION),
                len(KNOCKDOWN_FRAMES) - 1
            )
            frame_idx = KNOCKDOWN_FRAMES[knockdown_idx]
        else:
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
