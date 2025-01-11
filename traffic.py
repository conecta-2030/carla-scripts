#!/usr/bin/env python

import glob
import os
import sys
import time
import random
import argparse
import logging

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla


def get_actor_blueprints(world, filter_pattern, generation):
    blueprints = world.get_blueprint_library().filter(filter_pattern)
    if generation.lower() == "all":
        return blueprints

    try:
        generation = int(generation)
        return [bp for bp in blueprints if int(bp.get_attribute('generation')) == generation]
    except ValueError:
        logging.warning("Invalid generation specified. Using all available blueprints.")
        return blueprints


def main():
    argparser = argparse.ArgumentParser(description="Simplified pedestrian spawner for CARLA.")
    argparser.add_argument('--host', default='127.0.0.1', help='IP of the host server (default: 127.0.0.1)')
    argparser.add_argument('--port', default=2000, type=int, help='Port of the host server (default: 2000)')
    argparser.add_argument('--number-of-walkers', default=30, type=int, help='Number of walkers to spawn (default: 30)')
    argparser.add_argument('--filterw', default='walker.pedestrian.*', help='Filter for walkers (default: "walker.pedestrian.*")')
    argparser.add_argument('--generationw', default='2', help='Generation of walkers (default: 2)')
    argparser.add_argument('--seed', default=None, type=int, help='Random seed for reproducibility')
    argparser.add_argument('--synchronous', action='store_true', help='Enable synchronous mode')

    args = argparser.parse_args()

    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

    client = carla.Client(args.host, args.port)
    client.set_timeout(10.0)

    walkers_list = []
    all_id = []

    try:
        world = client.get_world()
        settings = world.get_settings()

        if args.synchronous:
            settings.synchronous_mode = True
            settings.fixed_delta_seconds = 0.05
            world.apply_settings(settings)
            logging.info("Synchronous mode enabled.")

        if args.seed:
            random.seed(args.seed)

        walker_blueprints = get_actor_blueprints(world, args.filterw, args.generationw)

        # Spawn walkers
        spawn_points = []
        retries = 5  # Max retries to generate valid spawn points

        for _ in range(args.number_of_walkers):
            for _ in range(retries):
                spawn_point = carla.Transform()
                location = world.get_random_location_from_navigation()
                if location:
                    spawn_point.location = location
                    spawn_points.append(spawn_point)
                    break
            else:
                logging.warning("Failed to find a valid spawn point after retries.")

        if len(spawn_points) < args.number_of_walkers:
            logging.warning(f"Only {len(spawn_points)} valid spawn points found. Requested: {args.number_of_walkers}")

        # Batch spawn walker actors
        walker_speed = []
        SpawnActor = carla.command.SpawnActor
        batch = []

        for spawn_point in spawn_points:
            walker_bp = random.choice(walker_blueprints)
            if walker_bp.has_attribute('is_invincible'):
                walker_bp.set_attribute('is_invincible', 'false')
            if walker_bp.has_attribute('speed'):
                walker_speed.append(float(walker_bp.get_attribute('speed').recommended_values[1]))
            else:
                walker_speed.append(1.0)
            batch.append(SpawnActor(walker_bp, spawn_point))

        results = client.apply_batch_sync(batch, True)
        for i, response in enumerate(results):
            if response.error:
                logging.error(f"Error spawning walker: {response.error}")
            else:
                walkers_list.append({"id": response.actor_id, "speed": walker_speed[i]})

        # Spawn walker controllers
        walker_controller_bp = world.get_blueprint_library().find('controller.ai.walker')
        batch = []

        for walker in walkers_list:
            batch.append(SpawnActor(walker_controller_bp, carla.Transform(), walker["id"]))

        results = client.apply_batch_sync(batch, True)
        for i, response in enumerate(results):
            if response.error:
                logging.error(f"Error spawning walker controller: {response.error}")
            else:
                walkers_list[i]["controller_id"] = response.actor_id

        # Start walker controllers
        all_id = [item for sublist in [[w["controller_id"], w["id"]] for w in walkers_list] for item in sublist]
        all_actors = world.get_actors(all_id)

        for i in range(0, len(all_id), 2):
            controller = all_actors[i]
            walker_speed = walkers_list[i // 2]["speed"]
            if hasattr(controller, 'start'):
                controller.start()
            controller.go_to_location(world.get_random_location_from_navigation())
            controller.set_max_speed(walker_speed)

        logging.info(f"Spawned {len(walkers_list)} walkers successfully.")

        while True:
            world.tick()

    finally:
        # Cleanup
        logging.info("Cleaning up walkers...")
        all_actors = world.get_actors(all_id)
        for i in range(0, len(all_id), 2):
            controller = all_actors[i]
            if hasattr(controller, 'stop'):
                controller.stop()

        client.apply_batch([carla.command.DestroyActor(x) for x in all_id])

        if args.synchronous:
            settings.synchronous_mode = False
            settings.fixed_delta_seconds = None
            world.apply_settings(settings)

        logging.info("Cleanup complete.")


if __name__ == '__main__':
    main()
