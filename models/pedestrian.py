import random
import threading
import time
import carla


class Pedestrian:
    """
    Represents a pedestrian in the simulation.
    Can move to a predefined destination or randomly within the map.
    """

    def __init__(self, world, start_location=None, end_location=None):
        """
        Initializes a pedestrian with optional start and end locations.
        If start_location is None, the pedestrian will spawn at a random location.
        If end_location is None, the pedestrian will move randomly.
        """
        self.world = world
        self.start_location = start_location or self._generate_random_location()
        self.end_location = end_location
        self.actor = None
        self.controller = None
        self.speed = random.uniform(1.0, 3.0)  # Random speed between 1 and 3 m/s

    def _generate_random_location(self):
        """
        Generates a random location within the map bounds.
        """
        spawn_points = self.world.get_map().get_spawn_points()
        random_point = random.choice(spawn_points)
        return random_point.location

    def spawn(self):
        """
        Spawns the pedestrian and assigns it a controller.
        """
        walker_bp = random.choice(self.world.get_blueprint_library().filter("walker.pedestrian.*"))
        controller_bp = self.world.get_blueprint_library().find('controller.ai.walker')

        # Convert start_location to a carla.Transform
        spawn_transform = carla.Transform(location=self.start_location)

        # Spawn pedestrian
        self.actor = self.world.try_spawn_actor(walker_bp, spawn_transform)
        if not self.actor:
            print(f"Failed to spawn pedestrian at {self.start_location}")
            return False

        # Spawn controller
        self.controller = self.world.try_spawn_actor(controller_bp, carla.Transform(), attach_to=self.actor)
        if not self.controller:
            print(f"Failed to spawn controller for pedestrian at {self.start_location}")
            self.actor.destroy()
            return False

        # Start walking
        self.controller.start()
        if self.end_location:
            self.controller.go_to_location(self.end_location)
        else:
            self._move_randomly()

        self.controller.set_max_speed(self.speed)
        print(f"Spawned pedestrian at {self.start_location}, moving with speed {self.speed:.2f} m/s")
        return True

    def _move_randomly(self):
        """
        Assigns a random destination periodically.
        """
        def assign_new_random_destination():
            while True:
                random_location = self._generate_random_location()
                self.controller.go_to_location(random_location)
                time.sleep(random.uniform(5, 10))  # Change direction every 5-10 seconds

        threading.Thread(target=assign_new_random_destination, daemon=True).start()

    def cleanup(self):
        """
        Cleans up the pedestrian and its controller.
        """
        if self.controller:
            self.controller.stop()
            self.controller.destroy()
        if self.actor:
            self.actor.destroy()