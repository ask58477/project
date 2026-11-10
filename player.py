from pico2d import load_image

# 2752 x 1536 원본 시트 기준 각 행(Row)·열(Frame)의 정확한 X 시작 좌표
# (캐릭터의 몸통 중심이 모든 프레임에서 동일하도록 정렬된 픽셀 값)
SPRITE_LEFT_TABLE = [
    [87, 511, 971, 1387],          # 0행 (맨 윗줄: IDLE 대기 4프레임)
    [94, 543, 1003, 1389, 1828],   # 1행 (두 번째 줄: SLASH 1 횡베기 5프레임)
    [101, 565, 992, 1435, 1874],   # 2행 (세 번째 줄: SLASH 2 회전강베기 5프레임)
    [86, 538, 974, 1407, 1873]     # 3행 (맨 아랫줄: PARRY 패링 5프레임)
]

BASE_SHEET_W = 2752.0
BASE_SHEET_H = 1536.0
CLIP_W = 440  # 검기 이펙트까지 짤리지 않는 1프레임 가로 폭
CLIP_H = 384  # 1536 / 4행 = 384px

# 인게임 화면에 출력할 캐릭터 크기 (원본의 절반 크기로 깔끔하게 출력)
DRAW_W = 220
DRAW_H = 192

class Player:
    def __init__(self):
        self.image = load_image('resources/player_sheet.png')
        # 이미지 해상도가 달라도 자동 보정되도록 스케일 비율 계산
        self.sx = self.image.w / BASE_SHEET_W
        self.sy = self.image.h / BASE_SHEET_H

        self.x = 640
        self.y = 260
        self.dir = 1        # 1: 우측, -1: 좌측
        self.frame = 0.0
        self.row = 0        # 0: 맨 윗줄(IDLE)

    def update(self, dt):
        pass

    def draw(self, cam_x=0, cam_y=0):
        frames_in_row = SPRITE_LEFT_TABLE[self.row]
        frame_idx = min(int(self.frame), len(frames_in_row) - 1)

        left = int(frames_in_row[frame_idx] * self.sx)
        bottom = int((3 - self.row) * CLIP_H * self.sy)
        w = int(CLIP_W * self.sx)
        h = int(CLIP_H * self.sy)

        flip = 'h' if self.dir == -1 else ''
        # 좌우 반전 시에도 몸통 중심이 어긋나지 않도록 미세 중심 보정
        offset_dir = 15 if self.dir == 1 else -15

        self.image.clip_composite_draw(
            left, bottom, w, h,
            0, flip,
            self.x + offset_dir + cam_x, self.y + cam_y,
            DRAW_W, DRAW_H
        )