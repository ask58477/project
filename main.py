from pico2d import open_canvas, close_canvas, clear_canvas, update_canvas, get_events
from pico2d import SDL_QUIT, SDL_KEYDOWN, SDLK_ESCAPE
import game_framework

SCREEN_W, SCREEN_H = 1280, 720

# Commit 3 테스트용 더미 상태 (Commit 4에서 play_state로 분리 예정)
class DummyState:
    @staticmethod
    def enter():
        pass

    @staticmethod
    def exit():
        pass

    @staticmethod
    def handle_events():
        events = get_events()
        for event in events:
            if event.type == SDL_QUIT:
                game_framework.quit()
            elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
                game_framework.quit()

    @staticmethod
    def update():
        pass

    @staticmethod
    def draw():
        clear_canvas()
        update_canvas()

if __name__ == '__main__':
    open_canvas(SCREEN_W, SCREEN_H)
    game_framework.run(DummyState)
    close_canvas()