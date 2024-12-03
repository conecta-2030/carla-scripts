import pygame
import carla
import numpy as np
import argparse
import random

def spawn_vehicle(world):
    blueprint_library = world.get_blueprint_library()

    spawn_points = world.get_map().get_spawn_points()
    random.shuffle(spawn_points)
    spawn_point = spawn_points[0]

    vehicle_bp = random.choice(blueprint_library.filter('vehicle.citroen.c3'))
    vehicle = world.spawn_actor(vehicle_bp,spawn_point)

    
    return vehicle

def main():
      try:
        argparser = argparse.ArgumentParser(
            description=__doc__)
        argparser.add_argument(
            '--host',
            metavar='H',
            default='127.0.0.1',
            help='IP of the host server (default: 127.0.0.1)')
        argparser.add_argument(
            '-p', '--port',
            metavar='P',
            default=2000,
            type=int,
            help='TCP port to listen to (default: 2000)')

        args = argparser.parse_args()
        #Conecta com o Carla
        client = carla.Client(args.host, args.port)
        #Tempo de espera
        client.set_timeout(2.0)
        #Pego o mundo do Carla, para consegui acessar config dele
        world = client.get_world()
        
        actor = spawn_vehicle(world)
        
      finally:
        print("Fechou sessão")

if __name__ == "__main__":
    main()