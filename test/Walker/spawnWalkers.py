import random
import time
import argparse
import carla

def spawn_pedestrians(world, num_pedestrians, pedestrian_names):
    spawned_pedestrians = []

    blueprint_library = world.get_blueprint_library()
    pedestrian_blueprints = []
    for name in pedestrian_names:
        pedestrian_blueprints.extend(blueprint_library.filter(name))

    spawn_points = world.get_map().get_spawn_points()
    random.shuffle(spawn_points)
    spawn_points = spawn_points[:num_pedestrians]

    for spawn_point in spawn_points:
        pedestrian_bp = random.choice(pedestrian_blueprints)
        pedestrian = world.spawn_actor(pedestrian_bp, spawn_point)
        spawned_pedestrians.append(pedestrian)

    return spawned_pedestrians

def main():
    try:
        argparser = argparse.ArgumentParser(description=__doc__)

        argparser.add_argument(
            '-f','--filterp',
            metavar='PATTERN',
            nargs='+',
            default=['walker.pedestrian.*'],
            help='Filter pedestrian model (default: "walker.pedestrian.*")')

        argparser.add_argument(
            '-n', '--num_pedestrians',
            type=int,
            default=10,
            help='Number of pedestrians to spawn (default: 10)')

        args = argparser.parse_args()

        client = carla.Client('localhost', 2000)
        client.set_timeout(2.0)

        world = client.get_world()

        num_pedestrians = args.num_pedestrians

        input("Pressione Enter para spawnar pedestres...")

        pedestrians = spawn_pedestrians(world, num_pedestrians, args.filterp)

        time.sleep(60)

    finally:
        print("Fechando conexão...")
        for pedestrian in pedestrians:
           pedestrian.destroy()

if __name__ == '__main__':
    main()
