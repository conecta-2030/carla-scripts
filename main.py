

# ==============================================================================
# -- find carla module ---------------------------------------------------------
# ==============================================================================


import glob
import os
import sys

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass


import argparse
import logging
import pygame
import carla
from world import World
from controls import DualControl
from hud import HUD
from controllers.pedestrian_manager import PedestrianManager


def game_loop(args):
    pygame.init()
    pygame.font.init()
    world = None

    try:
        client = carla.Client(args.host, args.port)
        client.set_timeout(10.0)

        display = pygame.display.set_mode(
            (args.width, args.height),
            pygame.HWSURFACE | pygame.DOUBLEBUF
        )

        hud = HUD(args.width, args.height)
        world = World(client.get_world(), hud, args.filter, args.weather)

        # Initialize PedestrianManager
        #pedestrian_manager = PedestrianManager(client, world.world)
        #pedestrian_manager.spawn_pedestrians(args.pedestrians)

        controller = DualControl(world, args.autopilot)

        clock = pygame.time.Clock()
        while True:
            clock.tick_busy_loop(30)
            if controller.parse_events(world, clock):
                return

            world.tick(clock)
            world.render(display)
            pygame.display.flip()

    finally:
        if world is not None:
            world.destroy()

        if 'pedestrian_manager' in locals():
            pedestrian_manager.cleanup()

        pygame.quit()

def main():
    argparser = argparse.ArgumentParser(description='CARLA Manual Control Client')
    argparser.add_argument('-v', '--verbose', action='store_true', dest='debug', help='print debug information')
    argparser.add_argument('--host', default='127.0.0.1', help='IP of the host server (default: 127.0.0.1)')
    argparser.add_argument('-p', '--port', default=2000, type=int, help='TCP port (default: 2000)')
    argparser.add_argument('-a', '--autopilot', action='store_true', help='enable autopilot')
    argparser.add_argument('--res', default='5760x1080', help='window resolution (default: 1930x1080)')
    argparser.add_argument('--filter', default='vehicle.*', help='actor filter (default: "vehicle.*")')
    argparser.add_argument('--weather', type=str, default=None, help='JSON string with weather parameters')
    argparser.add_argument(
    '--pedestrians',
    metavar='N',
    default=10,
    type=int,
    help='Number of pedestrians to spawn (default: 10)'
)
    args = argparser.parse_args()

    args.width, args.height = map(int, args.res.split('x'))

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level)

    logging.info('Listening to server %s:%s', args.host, args.port)

    try:
        game_loop(args)
    except KeyboardInterrupt:
        print('\nCancelled by user. Bye!')

if __name__ == '__main__':
    main()
