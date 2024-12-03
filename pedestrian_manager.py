import carla
import random

def spawn_pedestrian(world, start_location):
    """
    Spawns a pedestrian at the specified start location and positions the spectator camera.
    """
    # Get pedestrian blueprint
    walker_blueprints = world.get_blueprint_library().filter('walker.pedestrian.*')
    pedestrian_bp = random.choice(walker_blueprints)

    # Spawn the pedestrian
    transform = carla.Transform(start_location)
    pedestrian = world.spawn_actor(pedestrian_bp, transform)
    print(pedestrian_bp)
    print(transform)

    if pedestrian is None:
        print("Failed to spawn pedestrian.")
        return None, None

    print(f"Spawned pedestrian at {start_location}.")

    # Get walker controller blueprint
    controller_bp = world.get_blueprint_library().find('controller.ai.walker')
    pedestrian_controller = world.spawn_actor(controller_bp, carla.Transform(), pedestrian)

  

    return pedestrian, pedestrian_controller

def move_pedestrian(pedestrian_controller, end_location):
    """
    Moves a pedestrian to the specified end location.
    """
    if pedestrian_controller is not None and end_location is not None:
        pedestrian_controller.start()
        pedestrian_controller.go_to_location(end_location)
        pedestrian_controller.set_max_speed(2.0)
        print(f"Pedestrian is walking to {end_location}.")
    else:
        print("No pedestrian controller found to move.")

def track_pedestrian(world, pedestrian):
    if pedestrian is None:
        print("Pedestrian is not valid for tracking")
        return
    def print_location(event):
        location = pedestrian.get_location()
        print(f"Pedestrian is at: x{location.x:.2f}, y={location.y:.2f},z={location.z:.2f}")
    world.on_tick(print_location)