import carla
import random
import time
import argparse

def spawn_vehicles(world, num_vehicles, vehiclenames):
    # Lista para armazenar os veículos spawnados
    spawned_vehicles = []

    # Carregar blueprints dos veículos
    blueprint_library = world.get_blueprint_library()
    vehicle_blueprints = []
    for name in vehiclenames:
        vehicle_blueprints.extend(blueprint_library.filter(name))

    # Escolher spawn points aleatórios para os veículos
    spawn_points = world.get_map().get_spawn_points()
    random.shuffle(spawn_points)
    spawn_points = spawn_points[:num_vehicles]

    # Spawnar os veículos
    for spawn_point in spawn_points:
        vehicle_bp = random.choice(vehicle_blueprints)
        vehicle = world.spawn_actor(vehicle_bp, spawn_point)
        spawned_vehicles.append(vehicle)

    return spawned_vehicles

def main():
    try:
        argparser = argparse.ArgumentParser(description=__doc__)

        argparser.add_argument(
            '-f','--filterv',
            metavar='PATTERN',
            nargs='+',
            default=['vehicle.*'],
            help='Filter vehicle model (default: "vehicle.*")')

        argparser.add_argument(
            '-n', '--num_vehicles',
            type=int,
            default=10,
            help='Number of vehicles to spawn (default: 10)')

        args = argparser.parse_args()

        # Conectar ao simulador CARLA
        client = carla.Client('localhost', 2000)
        client.set_timeout(2.0) # Definir tempo limite para conexão

        # Carregar o mapa
        world = client.get_world()

        # Definir o número de veículos a serem spawnados
        num_vehicles = args.num_vehicles

        traffic_manager = client.get_trafficmanager()
        tm_port = traffic_manager.get_port()

        input("Pressione Enter para spawnar veículos...")

        # Chamar as funções para spawnar veículos
        vehicles = spawn_vehicles(world, num_vehicles, args.filterv)

        # Configurar os veículos para se moverem infinitamente
        for vehicle in vehicles:
            vehicle.set_autopilot(True, tm_port)

        # time.sleep(60)

    finally:
        print("Fechando conexão...")
        # for vehicle in vehicles:
        #    vehicle.destroy()

if __name__ == '__main__':
    main()

