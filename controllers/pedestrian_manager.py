from models.pedestrian import Pedestrian

class PedestrianManager:
    def __init__(self, world):
        self.world = world
        self.pedestrians = []

    def load_pedestrians(self, pedestrian_points):
        for start, end in pedestrian_points:
            pedestrian = Pedestrian(self.world, start, end)
            self.pedestrians.append(pedestrian)

    def spawn_pedestrians(self):
        for pedestrian in self.pedestrians:
            pedestrian.spawn()

    def spawn_random_pedestrians(self, count):
        for _ in range(count):
            pedestrian = Pedestrian(self.world)  # No start or end location specified
            if pedestrian.spawn():
                self.pedestrians.append(pedestrian)

    def cleanup(self):
        for pedestrian in self.pedestrians:
            pedestrian.cleanup()
        self.pedestrians = []