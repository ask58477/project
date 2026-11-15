from pico2d import load_image, draw_rectangle
from pico2d import SDL_KEYDOWN, SDLK_LEFT, SDLK_RIGHT, SDLK_a, SDLK_d

SPRITE_LEFT_TABLE = [
    [65, 505, 971],                # 프레임 경계에 맞춰 IDLE 컷 간 칼끝 겹침 방지
    [55, 508, 1003, 1389, 1828],   # 1행: SLASH 1 (5프레임)
    [0, 490, 992, 1435, 1910],    # 2행: SLASH 2 (5프레임)
    [86, 538, 974, 1407, 1873]     # 3행: PARRY (5프레임)
]

# Keep the character pivot stable after shifting the source crop per frame.
SLASH_DRAW_OFFSETS = {
    (1, 0): -20,
    (1, 1): -17,
    (2, 0): -50,
    (2, 1): -38,
    (2, 4): 18,
}

IDLE_DRAW_OFFSETS = {
    0: -11,
    1: -3,
}

BASE_SHEET_W = 2752.0
BASE_SHEET_H = 1536.0
CLIP_W = 440
CLIP_H = 384
DRAW_W = 220
DRAW_H = 192
PLAYER_HITBOX_HALF_W = 40
PLAYER_HITBOX_HALF_H = 55
MAX_HEALTH = 3
WHIFF_RECOVERY_DURATION = 0.25
PARRY_MISS_RECOVERY_DURATION = 0.1

class Player:
    def __init__(self):
        self.image = load_image('resources/player_sheet3.png')
        self.sx = self.image.w / BASE_SHEET_W
        self.sy = self.image.h / BASE_SHEET_H

        self.x = 640
        self.y = 260
        self.dir = 1
        self.state = 'IDLE'
        self.frame = 0.0
        self.row = 0
        self.max_health = MAX_HEALTH
        self.health = self.max_health
        self.slash_hit = False
        self.whiff_recovery = 0.0
        self.parry_hit = False
        self.parry_recovery = 0.0

    def start_slash(self, direction):
        if self.state in (
                'SLASH', 'PARRY', 'WHIFF_RECOVERY', 'PARRY_RECOVERY'):
            return

        self.dir = direction
        self.state = 'SLASH'
        self.frame = 0.0
        self.row = 1
        self.slash_hit = False

    def start_parry(self, direction):
        if self.state in (
                'SLASH', 'PARRY', 'WHIFF_RECOVERY', 'PARRY_RECOVERY'):
            return

        self.dir = direction
        self.state = 'PARRY'
        self.frame = 0.0
        self.row = 3
        self.parry_hit = False

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_LEFT:
                self.start_slash(-1)
            elif event.key == SDLK_RIGHT:
                self.start_slash(1)
            elif event.key == SDLK_a:
                self.start_parry(-1)
            elif event.key == SDLK_d:
                self.start_parry(1)

    def update(self, dt):
        if self.state == 'IDLE':
            self.row = 0
            self.frame = (self.frame + 6.0 * dt) % len(SPRITE_LEFT_TABLE[0])
        elif self.state == 'SLASH':
            slash_frame_count = len(SPRITE_LEFT_TABLE[1]) + len(SPRITE_LEFT_TABLE[2])
            if self.frame >= slash_frame_count:
                if self.slash_hit:
                    self.state = 'IDLE'
                    self.frame = 0.0
                    self.row = 0
                else:
                    self.state = 'WHIFF_RECOVERY'
                    self.whiff_recovery = WHIFF_RECOVERY_DURATION
                    self.frame = slash_frame_count - 1
                    self.row = 2
            else:
                self.frame += 18.0 * dt
                self.row = 1 if self.frame < len(SPRITE_LEFT_TABLE[1]) else 2
        elif self.state == 'PARRY':
            if self.frame >= len(SPRITE_LEFT_TABLE[3]):
                if self.parry_hit:
                    self.state = 'IDLE'
                    self.frame = 0.0
                    self.row = 0
                else:
                    self.state = 'PARRY_RECOVERY'
                    self.parry_recovery = PARRY_MISS_RECOVERY_DURATION
                    self.frame = len(SPRITE_LEFT_TABLE[3]) - 1
                    self.row = 3
            else:
                self.frame += 18.0 * dt
        elif self.state == 'WHIFF_RECOVERY':
            self.whiff_recovery = max(0.0, self.whiff_recovery - dt)
            if self.whiff_recovery == 0.0:
                self.state = 'IDLE'
                self.frame = 0.0
                self.row = 0
        elif self.state == 'PARRY_RECOVERY':
            self.parry_recovery = max(0.0, self.parry_recovery - dt)
            if self.parry_recovery == 0.0:
                self.state = 'IDLE'
                self.frame = 0.0
                self.row = 0

    def register_slash_hit(self):
        if self.state == 'SLASH':
            self.slash_hit = True

    def register_parry_hit(self):
        if self.state == 'PARRY':
            self.parry_hit = True

    def draw(self, cam_x=0, cam_y=0):
        frames_in_row = SPRITE_LEFT_TABLE[self.row]
        frame_idx = int(self.frame)
        if self.state in ('SLASH', 'WHIFF_RECOVERY') and self.row == 2:
            frame_idx -= len(SPRITE_LEFT_TABLE[1])
        frame_idx = min(frame_idx, len(frames_in_row) - 1)

        left = int(frames_in_row[frame_idx] * self.sx)
        bottom = int((3 - self.row) * CLIP_H * self.sy)
        w = int(CLIP_W * self.sx)
        h = int(CLIP_H * self.sy)

        flip = 'h' if self.dir == -1 else ''
        offset_dir = 15 if self.dir == 1 else -15
        draw_x = self.x + offset_dir + cam_x
        if self.state == 'IDLE':
            draw_x += self.dir * IDLE_DRAW_OFFSETS.get(frame_idx, 0)
        if self.state in ('SLASH', 'WHIFF_RECOVERY'):
            draw_x += self.dir * SLASH_DRAW_OFFSETS.get((self.row, frame_idx), 0)

        self.image.clip_composite_draw(
            left, bottom, w, h,
            0, flip,
            draw_x, self.y + cam_y,
            DRAW_W, DRAW_H
        )

    def get_slash_hitbox(self):
        if self.state != 'SLASH':
            return None

        near_x = self.x + self.dir * 50
        far_x = self.x + self.dir * 160
        return (
            min(near_x, far_x),
            self.y - 73,
            max(near_x, far_x),
            self.y + 65
        )

    def get_parry_hitbox(self):
        if self.state != 'PARRY':
            return None

        near_x = self.x + self.dir * 50
        far_x = self.x + self.dir * 160
        return (
            min(near_x, far_x),
            self.y - 73,
            max(near_x, far_x),
            self.y + 65
        )

    def get_hitbox(self):
        return (
            self.x - PLAYER_HITBOX_HALF_W,
            self.y - PLAYER_HITBOX_HALF_H,
            self.x + PLAYER_HITBOX_HALF_W,
            self.y + PLAYER_HITBOX_HALF_H
        )

    def take_damage(self):
        if self.health <= 0:
            return False

        self.health -= 1
        return True

    def draw_health(self, cam_x=0, cam_y=0):
        segment_w, segment_h, gap = 30, 12, 4
        total_width = self.max_health * segment_w + (self.max_health - 1) * gap
        left = self.x - total_width / 2 + cam_x
        bottom = self.y + DRAW_H / 2 - 32 + cam_y
        for index in range(self.max_health):
            color = (220, 48, 48) if index < self.health else (70, 70, 70)
            segment_left = left + index * (segment_w + gap)
            draw_rectangle(
                segment_left, bottom,
                segment_left + segment_w, bottom + segment_h,
                *color, filled=True
            )

        draw_rectangle(
            left - 3, bottom - 3,
            left + total_width + 3, bottom + segment_h + 3,
            235, 235, 235
        )

    def draw_hit_zone(self, cam_x=0, cam_y=0):
        hitbox = self.get_slash_hitbox()
        if hitbox is None:
            return

        zone_left, zone_bottom, zone_right, zone_top = hitbox
        zone_left += cam_x
        zone_right += cam_x
        zone_bottom += cam_y
        zone_top += cam_y
        px = self.x + cam_x
        py = self.y + cam_y
        near_x = px + self.dir * 50
        perfect_x = px + self.dir * 110
        perfect_left = min(near_x, perfect_x)
        perfect_right = max(near_x, perfect_x)

        draw_rectangle(
            zone_left, zone_bottom, zone_right, zone_top,
            0, 255, 255
        )
        draw_rectangle(
            perfect_left, py - 68, perfect_right, py - 58,
            255, 0, 220
        )