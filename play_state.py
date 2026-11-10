from pico2d import clear_canvas, update_canvas, get_events
from pico2d import SDL_QUIT, SDL_KEYDOWN, SDLK_ESCAPE
import game_framework

# 인게임 전역 타이머 및 속도 배율 변수
stage_timer = 0.0
game_speed = 1.0

def enter():
    global stage_timer, game_speed
    stage_timer = 0.0
    game_speed = 1.0
    print("PlayState 진입 완료")

def exit():
    print("PlayState 종료")

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

def update():
    global stage_timer
    # Delta Time에 게임 속도 배율을 곱해 시간 누적
    dt = game_framework.frame_time * game_speed
    stage_timer += dt

def draw():
    clear_canvas()
    # Phase 2에서 이곳에 배경 및 Player.draw()가 추가됩니다.
    update_canvas()