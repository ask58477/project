from pico2d import load_image, draw_rectangle
from pico2d import SDL_KEYDOWN, SDLK_LEFT, SDLK_RIGHT, SDLK_a, SDLK_d

SPRITE_LEFT_TABLE = [
    [87, 511, 971, 1387],          # 0행: IDLE (4프레임)
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

BASE_SHEET_W = 2752.0
BASE_SHEET_H = 1536.0
CLIP_W = 440
CLIP_H = 384
DRAW_W = 220
DRAW_H = 192

class Player:
    def __init__(self):
        self.image = load_image('resources/player_sheet2.png')
        self.sx = self.image.w / BASE_SHEET_W
        self.sy = self.image.h / BASE_SHEET_H

        self.x = 640
        self.y = 260
        self.dir = 1
        self.state = 'IDLE'
        self.frame = 0.0
        self.row = 0

    def start_slash(self, direction):
        self.dir = direction
        self.state = 'SLASH'
        self.frame = 0.0
        self.row = 1

    def start_parry(self, direction):
        self.dir = direction
        self.state = 'PARRY'
        self.frame = 0.0
        self.row = 3

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
            self.frame += 18.0 * dt
            slash_frame_count = len(SPRITE_LEFT_TABLE[1]) + len(SPRITE_LEFT_TABLE[2])
            if self.frame >= slash_frame_count:
                self.state = 'IDLE'
                self.frame = 0.0
                self.row = 0
            else:
                self.row = 1 if self.frame < len(SPRITE_LEFT_TABLE[1]) else 2
        elif self.state == 'PARRY':
            self.frame += 18.0 * dt
            if self.frame >= len(SPRITE_LEFT_TABLE[3]):
                self.state = 'IDLE'
                self.frame = 0.0
                self.row = 0

    def draw(self, cam_x=0, cam_y=0):
        frames_in_row = SPRITE_LEFT_TABLE[self.row]
        frame_idx = int(self.frame)
        if self.state == 'SLASH' and self.row == 2:
            frame_idx -= len(SPRITE_LEFT_TABLE[1])
        frame_idx = min(frame_idx, len(frames_in_row) - 1)

        left = int(frames_in_row[frame_idx] * self.sx)
        bottom = int((3 - self.row) * CLIP_H * self.sy)
        w = int(CLIP_W * self.sx)
        h = int(CLIP_H * self.sy)

        flip = 'h' if self.dir == -1 else ''
        offset_dir = 15 if self.dir == 1 else -15
        draw_x = self.x + offset_dir + cam_x
        if self.state == 'SLASH':
            draw_x += self.dir * SLASH_DRAW_OFFSETS.get((self.row, frame_idx), 0)

        self.image.clip_composite_draw(
            left, bottom, w, h,
            0, flip,
            draw_x, self.y + cam_y,
            DRAW_W, DRAW_H
        )

    def draw_hit_zone(self, cam_x=0, cam_y=0):
        px = self.x + cam_x
        py = self.y + cam_y

        # 바닥 기준선 (캐릭터 발바닥 높이에 맞춤)
        draw_rectangle(0, py - 75, 1280, py - 73)

        # 좌측 판정 영역 (-160px ~ -50px) 및 PERFECT 구간 (-110px ~ -50px)
        draw_rectangle(px - 160, py - 73, px - 50, py + 65)
        draw_rectangle(px - 110, py - 68, px - 50, py - 58)

        # 우측 판정 영역 (+50px ~ +160px) 및 PERFECT 구간 (+50px ~ +110px)
        draw_rectangle(px + 50, py - 73, px + 160, py + 65)
        draw_rectangle(px + 50, py - 68, px + 110, py - 58)