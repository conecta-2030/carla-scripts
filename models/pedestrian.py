import random
import carla
import threading
import time


class Pedestrian:
    """
    Represents a pedestrian in the CARLA simulation.
    """

    def __init__(self, world, start_location=None):
        """
        Initializes a pedestrian instance.

        :param world: The CARLA simulation world.
        :param start_location: Optional starting location for the pedestrian.
        """
        self.world = world
        self.actor = None
        self.controller = None
        self.start_location = start_location or self._get_random_spawn_location()
        self.speed = random.uniform(1.0, 3.0)  # Random walking speed

    def _get_random_spawn_location(self):
        """
        Gets a random spawn location from the map's spawn points.
        """
        spawn_points = self.world.get_map().get_spawn_points()
        return random.choice(spawn_points).location

    def spawn(self):
        walker_bp = random.choice(self.world.get_blueprint_library().filter("walker.pedestrian.*"))
        controller_bp = self.world.get_blueprint_library().find("controller.ai.walker")

        # Spawn pedestrian actor
        spawn_transform = carla.Transform(location=self.start_location)
        self.actor = self.world.try_spawn_actor(walker_bp, spawn_transform)
        if not self.actor:
            print(f"[ERROR] Failed to spawn pedestrian at {self.start_location}")
            return False

        # Spawn walker controller
        self.controller = self.world.try_spawn_actor(controller_bp, carla.Transform(), attach_to=self.actor)
        if not self.controller:
            print(f"[ERROR] Failed to spawn controller for pedestrian at {self.start_location}")
            self.actor.destroy()
            return False

        # Set walking behavior
        self.controller.start()
        self.controller.set_max_speed(self.speed)
        print(f"[DEBUG] Pedestrian spawned at {self.start_location} with speed {self.speed:.2f} m/s")

        # Assign random destinations
        threading.Thread(target=self._assign_random_walk, daemon=True).start()
        return True

    def _assign_random_walk(self):
        """
        Assigns random destinations periodically to the pedestrian.
        """
        while self.actor.is_alive:
            destination = self._get_random_spawn_location()
            self.controller.go_to_location(destination)
            time.sleep(random.uniform(5, 15))  # Change direction every 5-15 seconds

    def cleanup(self):
        """
        Destroys the pedestrian and its controller.
        """
        if self.controller:
            self.controller.stop()
            self.controller.destroy()
        if self.actor:
            self.actor.destroy()
