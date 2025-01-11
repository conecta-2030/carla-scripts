import carla
import random

class PedestrianManager:
    def __init__(self, client, world):
        self.client = client
        self.world = world
        self.walkers_list = []
        self.all_id = []

    def spawn_pedestrians(self, number_of_walkers=10):
        try:
            print(f"Spawning {number_of_walkers} pedestrians...")
            blueprints = self.world.get_blueprint_library().filter("walker.pedestrian.*")
            spawn_points = []

            # Generate random spawn points for pedestrians
            for _ in range(number_of_walkers):
                loc = self.world.get_random_location_from_navigation()
                if loc:
                    spawn_points.append(carla.Transform(loc))

            # Batch for spawning pedestrian actors
            batch = []
            walker_speed = []
            for spawn_point in spawn_points:
                walker_bp = random.choice(blueprints)

                # Set pedestrian attributes
                if walker_bp.has_attribute("is_invincible"):
                    walker_bp.set_attribute("is_invincible", "false")
                if walker_bp.has_attribute("speed"):
                    walker_speed.append(float(walker_bp.get_attribute("speed").recommended_values[1]))
                else:
                    walker_speed.append(1.0)  # Default walking speed

                batch.append(carla.command.SpawnActor(walker_bp, spawn_point))

            # Process the spawn batch in chunks to avoid timeout
            chunk_size = 10
            for i in range(0, len(batch), chunk_size):
                results = self.client.apply_batch_sync(batch[i:i + chunk_size], True)
                for result in results:
                    if result.error:
                        print(f"[ERROR] {result.error}")
                    else:
                        self.walkers_list.append({"id": result.actor_id})

            # Spawn walker controllers
            walker_controller_bp = self.world.get_blueprint_library().find("controller.ai.walker")
            batch = []
            for walker in self.walkers_list:
                batch.append(carla.command.SpawnActor(walker_controller_bp, carla.Transform(), walker["id"]))

            results = self.client.apply_batch_sync(batch, True)
            for i in range(len(results)):
                if results[i].error:
                    print(f"[ERROR] {results[i].error}")
                else:
                    self.walkers_list[i]["con"] = results[i].actor_id

            # Initialize walker controllers and assign random destinations
            for walker in self.walkers_list:
                walker_actor = self.world.get_actor(walker["con"])
                walker_actor.start()
                walker_actor.go_to_location(self.world.get_random_location_from_navigation())
                walker_actor.set_max_speed(random.uniform(0.5, 1.5))  # Set random walking speed

            print(f"Successfully spawned {len(self.walkers_list)} pedestrians!")

        except Exception as e:
            print(f"Error spawning pedestrians: {e}")

    def cleanup(self):
        # Stop and destroy all walkers and controllers
        all_actors = self.world.get_actors(self.all_id)
        for actor in all_actors:
            actor.destroy()
        self.walkers_list = []
        self.all_id = []
        print("Cleaned up all pedestrians.")
