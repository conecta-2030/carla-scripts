
import carla
import argparse
import random
import pygame
import numpy as np

def spawn_vehicle(world):
    blueprint_library = world.get_blueprint_library()

    spawn_points = world.get_map().get_spawn_points()
    random.shuffle(spawn_points)
    spawn_point = spawn_points[0]

    vehicle_bp = random.choice(blueprint_library.filter('vehicle.citroen.c3'))

    print(vehicle_bp)
    if vehicle_bp.has_attribute('color'):
        color = vehicle_bp.get_attribute('color').recommended_values[1]
        vehicle_bp.set_attribute('color', color)

    vehicle = world.spawn_actor(vehicle_bp,spawn_point)


    return vehicle

class RenderObject(object):
    def __init__(self, width, height):
        init_image = np.random.randint(0,255,(height,width,3),dtype='uint8')
        self.surface = pygame.surfarray.make_surface(init_image.swapaxes(0,1))

# Camera sensor callback, reshapes raw data from camera into 2D RGB and applies to PyGame surface
def pygame_callback(data, obj):
    img = np.reshape(np.copy(data.raw_data), (data.height, data.width, 4))
    img = img[:,:,:3]
    img = img[:, :, ::-1]
    obj.surface = pygame.surfarray.make_surface(img.swapaxes(0,1))

def spawnVehicles(world):
    spawn_points = world.get_map().get_spawn_points()

    # Select some models from the blueprint library
    models = ['dodge', 'audi', 'model3', 'mini', 'mustang', 'lincoln', 'prius', 'nissan', 'crown', 'impala']
    blueprints = []
    for vehicle in world.get_blueprint_library().filter('*vehicle*'):
        if any(model in vehicle.id for model in models):
            blueprints.append(vehicle)

    # Set a max number of vehicles and prepare a list for those we spawn
    max_vehicles = 10
    max_vehicles = min([max_vehicles, len(spawn_points)])
    vehicles = []

    # Take a random sample of the spawn points and spawn some vehicles
    for i, spawn_point in enumerate(random.sample(spawn_points, max_vehicles)):
        temp = world.try_spawn_actor(random.choice(blueprints), spawn_point)
        if temp is not None:
            vehicles.append(temp)

    return vehicles

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

        ## Metodo que retorna um veiculo que foi spawnado
        actor = spawn_vehicle(world)

        #Exemplo de pegar parametros do carro
        print(actor.get_acceleration())
        print(actor.get_velocity())

        
        traffic_manager = client.get_trafficmanager()
        tm_port = traffic_manager.get_port()

        actor.set_autopilot(True,tm_port)
        #traffic_manager.ignore_lights_percentage(actor, random.randint(0,1))

        traffic_manager.global_percentage_speed_difference(2.0)

        vehicles = spawnVehicles(world)

        for vehicle in vehicles:
            vehicle.set_autopilot(True,tm_port)
            physics_controlFor = vehicle.get_physics_control()
            physics_controlFor.use_sweep_wheel_collision = True
            vehicle.apply_physics_control(physics_controlFor)
            # Randomly set the probability that a vehicle will ignore traffic lights
            #traffic_manager.ignore_lights_percentage(vehicle, random.randint(0,50))

        # Initialise the camera floating behind the vehicle
        camera_init_trans = carla.Transform(carla.Location(x=1, z=1.5), carla.Rotation(pitch=-20))
        camera_bp = world.get_blueprint_library().find('sensor.camera.rgb')
        #Tipo de objeto, position, filho de um objeto
        camera = world.spawn_actor(camera_bp, camera_init_trans, attach_to=actor)

        # Start camera with PyGame callback
        camera.listen(lambda image: pygame_callback(image, renderObject))

        # Get camera dimensions
        image_w = camera_bp.get_attribute("image_size_x").as_int()
        image_h = camera_bp.get_attribute("image_size_y").as_int()

        # Instantiate objects for rendering and vehicle control
        renderObject = RenderObject(image_w, image_h)
    
        # Initialise the display
        pygame.init()
        gameDisplay = pygame.display.set_mode((image_w,image_h), pygame.HWSURFACE | pygame.DOUBLEBUF)
        # Draw black to the display
        gameDisplay.fill((0,0,0))
        gameDisplay.blit(renderObject.surface, (0,0))
        pygame.display.flip()
        
        # Game loop
        crashed = False

        m = 1600
        Cx = 0.23
        physics_control = actor.get_physics_control()
        physics_control.use_sweep_wheel_collision = True
        actor.apply_physics_control(physics_control)

        #Config Physic
        # physics_control = vehicle.get_physics_control()
        # physics_control.mass = m
        # physics_control.drag_coefficient = Cx
        # vehicle.apply_physics_control(physics_control)

        while not crashed:
            # Advance the simulation time
            world.tick()
            # Update the display
            gameDisplay.blit(renderObject.surface, (0,0))
            pygame.display.flip()
            # Process the current control state
            # Collect key press events
            for event in pygame.event.get():
                # If the window is closed, break the while loop
                if event.type == pygame.QUIT:
                    crashed = True
            

        # Stop camera and quit PyGame after exiting game loop
        camera.stop()
        pygame.quit()   
        actor.destroy()
        for vehicle in vehicles:
            vehicle.destroy()
            
    
    finally:
        print("Fechou")
        actor.destroy()
        for vehicle in vehicles:
            vehicle.destroy()

    
if __name__ == '__main__':

    main()
