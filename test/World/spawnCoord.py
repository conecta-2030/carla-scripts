import carla
import random
import argparse
import time

def spawn_actor_at_location(client, blueprint_library, spawn_point, actor_type):
    if actor_type == "car":
        actor_bp = random.choice(blueprint_library.filter("vehicle.*"))
    elif actor_type == "walker":
        actor_bp = random.choice(blueprint_library.filter("walker.pedestrian.*"))
    else:
        raise ValueError("Invalid actor type. Please choose 'vehicle' or 'pedestrian'.")

    actor = client.get_world().try_spawn_actor(actor_bp, spawn_point)
    actor.set_transform(carla.Transform(spawn_point.location, spawn_point.rotation))
    return actor

def main(args):
    try:
        client = carla.Client(args.host, args.port)
        client.set_timeout(2.0)
        world = client.get_world()
        blueprint_library = world.get_blueprint_library()

        # Convertendo as coordenadas de metros para centímetros
        x_cm = args.x / 100
        y_cm = args.y / 100
        z_cm = args.z / 100

        spawn_point = carla.Transform(carla.Location(x=x_cm, y=y_cm, z=z_cm))
        actor = spawn_actor_at_location(client, blueprint_library, spawn_point, args.t)

        if actor is not None:
            print(f"{args.actor_type.capitalize()} spawnado com sucesso!")
        else:
            print("Falha ao spawnar o ator. Verifique as coordenadas e o tipo de ator.")

        # time.sleep(100)

    finally:
        print("Fechando conexão...")
        # if actor is not None:
        #     actor.destroy()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Spawn NPC in CARLA at specified coordinates")
    parser.add_argument('--host', default='localhost', help='CARLA server host')
    parser.add_argument('--port', default=2000, type=int, help='CARLA server port')
    parser.add_argument('-x', type=float, help='X coordinate of spawn location in meters')
    parser.add_argument('-y', type=float, help='Y coordinate of spawn location in meters')
    parser.add_argument('-z', type=float, help='Z coordinate of spawn location in meters')
    parser.add_argument('-t', choices=['car', 'walker'], default='vehicle', help="Type of actor to spawn")
    args = parser.parse_args()

    main(args)
