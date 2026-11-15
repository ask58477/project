from pico2d import load_image


FRAME_W = 400
FRAME_H = 335
FRAME_COUNT = 3
KNOCKDOWN_FRAME_DURATION = 0.12
DRAW_W = 220
DRAW_H = 184
HITBOX_HALF_W = 40
HITBOX_HALF_H = 55
SPAWN_LEFT_X = -100
SPAWN_RIGHT_X = 1380


class Enemy:
    SPEED = 360
    DEATH_KNOCKBACK_SPEED = 1400
    KNOCKBACK_DECELERATION = 500
    KNOCKBACK_LIFT = 450
    KNOCKBACK_GRAVITY = 1200
    KNOCKBACK_SPIN_SPEED = 16
    KNOCKBACK_SPIN_DECELERATION = 3
    SPRITE_ROW = 0
    KNOCKDOWN_ROW = 0
    KNOCKDOWN_FRAMES = (4, 3, 5)

    def __init__(self, target_x, y, direction=-1):
        if direction not in (-1, 1):
            raise ValueError('direction must be -1 or 1')

        self.image = load_image('resources/enemy.png')
        self.direction = direction
        self.x = SPAWN_RIGHT_X if direction == -1 else SPAWN_LEFT_X
        self.y = y
        self.target_x = target_x
        self.speed = self.SPEED
        self.sprite_row = self.SPRITE_ROW
        self.knockdown_row = self.KNOCKDOWN_ROW
        self.knockdown_frames = self.KNOCKDOWN_FRAMES
        self.frame = 0.0
        self.state = 'APPROACH'
        self.knockdown_elapsed = 0.0
        self.knockback_active = False
        self.knockback_velocity_x = 0.0
        self.knockback_velocity_y = 0.0
        self.rotation = 0.0
        self.rotation_speed = 0.0

    def update(self, dt):
        if self.state == 'KNOCKED_DOWN':
            self.knockdown_elapsed = min(
                self.knockdown_elapsed + dt,
                len(self.knockdown_frames) * KNOCKDOWN_FRAME_DURATION
            )
            if self.knockback_active:
                speed = abs(self.knockback_velocity_x)
                direction = 1 if self.knockback_velocity_x > 0 else -1
                deceleration_time = min(
                    dt, speed / self.KNOCKBACK_DECELERATION
                )
                self.x += direction * (
                    speed * deceleration_time -
                    0.5 * self.KNOCKBACK_DECELERATION *
                    deceleration_time ** 2
                )
                next_speed = max(
                    0.0, speed - self.KNOCKBACK_DECELERATION * dt
                )
                self.knockback_velocity_x = direction * next_speed
                self.y += (
                    self.knockback_velocity_y * dt -
                    0.5 * self.KNOCKBACK_GRAVITY * dt ** 2
                )
                self.knockback_velocity_y -= self.KNOCKBACK_GRAVITY * dt

                spin_sign = 1 if self.rotation_speed >= 0 else -1
                spin_speed = abs(self.rotation_speed)
                spin_deceleration_time = min(
                    dt,
                    spin_speed / self.KNOCKBACK_SPIN_DECELERATION
                )
                self.rotation += spin_sign * (
                    spin_speed * spin_deceleration_time -
                    0.5 * self.KNOCKBACK_SPIN_DECELERATION *
                    spin_deceleration_time ** 2
                )
                spin_speed = max(
                    0.0,
                    spin_speed - self.KNOCKBACK_SPIN_DECELERATION * dt
                )
                self.rotation_speed = spin_sign * spin_speed
            return
        if self.state != 'APPROACH':
            return

        self.frame = (self.frame + 8.0 * dt) % FRAME_COUNT
        if self.direction == -1:
            self.x = max(self.target_x, self.x - self.speed * dt)
        else:
            self.x = min(self.target_x, self.x + self.speed * dt)

    @property
    def is_finished(self):
        if self.state == 'KNOCKED_DOWN' and self.knockback_active:
            return self.x < SPAWN_LEFT_X or self.x > SPAWN_RIGHT_X
        return (
            self.state == 'KNOCKED_DOWN' and
            self.knockdown_elapsed >=
            len(self.knockdown_frames) * KNOCKDOWN_FRAME_DURATION
        )

    def hit_by_slash(self, hitbox):
        return self.knock_down_if_overlapping(hitbox)

    def hit_by_parry(self, hitbox):
        return False

    def knock_down_if_overlapping(self, hitbox):
        if self.state != 'APPROACH':
            return False

        if not self.overlaps_hitbox(hitbox):
            return False

        self.knock_down(knockback=True)
        return True

    def knock_down(self, knockback=False):
        self.state = 'KNOCKED_DOWN'
        self.knockdown_elapsed = 0.0
        self.knockback_active = knockback
        self.rotation = 0.0
        if knockback:
            self.knockback_velocity_x = (
                -self.direction * self.DEATH_KNOCKBACK_SPEED
            )
            self.knockback_velocity_y = self.KNOCKBACK_LIFT
            self.rotation_speed = (
                self.direction * self.KNOCKBACK_SPIN_SPEED
            )

    def overlaps_hitbox(self, hitbox):
        left, bottom, right, top = hitbox
        enemy_left = self.x - HITBOX_HALF_W
        enemy_right = self.x + HITBOX_HALF_W
        enemy_bottom = self.y - HITBOX_HALF_H
        enemy_top = self.y + HITBOX_HALF_H
        return not (
            enemy_left > right or enemy_right < left or
            enemy_bottom > top or enemy_top < bottom
        )

    def draw(self):
        if self.state == 'KNOCKED_DOWN':
            knockdown_idx = min(
                int(self.knockdown_elapsed / KNOCKDOWN_FRAME_DURATION),
                len(self.knockdown_frames) - 1
            )
            frame_idx = self.knockdown_frames[knockdown_idx]
            sprite_row = self.knockdown_row
        else:
            frame_idx = int(self.frame)
            sprite_row = self.sprite_row
        self.image.clip_composite_draw(
            frame_idx * FRAME_W,
            self.image.h - (sprite_row + 1) * FRAME_H,
            FRAME_W,
            FRAME_H,
            self.rotation,
            'h' if self.direction == -1 else '',
            self.x,
            self.y,
            DRAW_W,
            DRAW_H
        )


class YellowEnemy(Enemy):
    SPEED = Enemy.SPEED * 0.8
    SPRITE_ROW = 1
    KNOCKDOWN_ROW = 1
    KNOCKDOWN_FRAMES = (3, 4, 5)

    def hit_by_slash(self, hitbox):
        return False

    def hit_by_parry(self, hitbox):
        return self.knock_down_if_overlapping(hitbox)


class RedEnemy(Enemy):
    SPEED = Enemy.SPEED * 1.8
    SPRITE_ROW = 2
    KNOCKDOWN_ROW = 3
    KNOCKDOWN_FRAMES = (4, 5)
    PARRY_REACTION_FRAMES = 4
    PARRY_REACTION_DURATION = 0.12
    COUNTERATTACK_FRAMES = (3, 4, 5)
    KNOCKBACK_DISTANCE = 60
    KNOCKBACK_SPEED = 180

    def __init__(self, target_x, y, direction=-1):
        super().__init__(target_x, y, direction)
        self.has_been_parried = False
        self.state_elapsed = 0.0
        self.knockback_target_x = self.x

    def update(self, dt):
        if self.state in ('APPROACH', 'KNOCKED_DOWN'):
            super().update(dt)
            return

        self.state_elapsed += dt
        if self.state == 'PARRIED':
            self.sprite_row = 3
            self.frame = min(
                int(self.state_elapsed / self.PARRY_REACTION_DURATION),
                self.PARRY_REACTION_FRAMES - 1
            )
            if self.direction == -1:
                self.x = min(
                    self.knockback_target_x,
                    self.x + self.KNOCKBACK_SPEED * dt
                )
            else:
                self.x = max(
                    self.knockback_target_x,
                    self.x - self.KNOCKBACK_SPEED * dt
                )
            if self.state_elapsed >= (
                    self.PARRY_REACTION_FRAMES *
                    self.PARRY_REACTION_DURATION):
                self.state = 'COUNTERATTACK'
                self.state_elapsed = 0.0
                self.sprite_row = 2
                self.frame = self.COUNTERATTACK_FRAMES[0]
        elif self.state == 'COUNTERATTACK':
            self.sprite_row = 2
            frame_idx = min(
                int(self.state_elapsed / self.PARRY_REACTION_DURATION),
                len(self.COUNTERATTACK_FRAMES) - 1
            )
            self.frame = self.COUNTERATTACK_FRAMES[frame_idx]
            if self.state_elapsed >= (
                    len(self.COUNTERATTACK_FRAMES) *
                    self.PARRY_REACTION_DURATION):
                self.state = 'APPROACH'
                self.state_elapsed = 0.0
                self.sprite_row = 2
                self.frame = 0.0

    def hit_by_slash(self, hitbox):
        if (not self.has_been_parried or
                self.state == 'KNOCKED_DOWN' or
                not self.overlaps_hitbox(hitbox)):
            return False

        self.knock_down(knockback=True)
        return True

    def hit_by_parry(self, hitbox):
        if (self.state != 'APPROACH' or self.has_been_parried or
                not self.overlaps_hitbox(hitbox)):
            return False

        self.has_been_parried = True
        self.state = 'PARRIED'
        self.state_elapsed = 0.0
        self.sprite_row = 3
        self.frame = 0.0
        self.knockback_target_x = (
            self.x - self.direction * self.KNOCKBACK_DISTANCE
        )
        return True
