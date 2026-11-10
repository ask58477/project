from pico2d import open_canvas, close_canvas
import game_framework
import play_state

SCREEN_W, SCREEN_H = 1280, 720

if __name__ == '__main__':
    open_canvas(SCREEN_W, SCREEN_H)
    game_framework.run(play_state)
    close_canvas()