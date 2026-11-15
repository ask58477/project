from enemy import Enemy, YellowEnemy, RedEnemy


# Direction is the travel direction: -1 enters from the right, +1 from the left.
DEFAULT_SPAWN_SCHEDULE = (
    (1.0, Enemy, -1),
    (2.0, YellowEnemy, 1),
    (3.0, RedEnemy, -1),
)


class SpawnManager:
    def __init__(self, schedule=None):
        events = DEFAULT_SPAWN_SCHEDULE if schedule is None else schedule
        self.schedule = tuple(sorted(events, key=lambda event: event[0]))
        self.reset()

    def reset(self):
        self.elapsed = 0.0
        self.next_event = 0

    def update(self, dt, player):
        self.elapsed += dt
        spawned = []

        while self.next_event < len(self.schedule):
            spawn_time, enemy_type, direction = self.schedule[self.next_event]
            if self.elapsed < spawn_time:
                break

            target_x = player.x - direction * 80
            spawned.append(enemy_type(target_x, player.y, direction))
            self.next_event += 1

        return spawned
