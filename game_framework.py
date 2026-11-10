import time

running = None
stack = None
frame_time = 0.0

def change_state(state):
    global stack
    if len(stack) > 0:
        stack[-1].exit()
        stack.pop()
    stack.append(state)
    state.enter()

def push_state(state):
    global stack
    if len(stack) > 0:
        stack[-1].pause()
    stack.append(state)
    state.enter()

def pop_state():
    global stack
    if len(stack) > 0:
        stack[-1].exit()
        stack.pop()
    if len(stack) > 0:
        stack[-1].resume()

def quit():
    global running
    running = False

def run(start_state):
    global running, stack, frame_time
    running = True
    stack = [start_state]
    start_state.enter()

    current_time = time.time()
    while running:
        # Delta Time (frame_time) 계산
        new_time = time.time()
        frame_time = new_time - current_time
        current_time = new_time

        stack[-1].handle_events()
        stack[-1].update()
        stack[-1].draw()

    while len(stack) > 0:
        stack[-1].exit()
        stack.pop()