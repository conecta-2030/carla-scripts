
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


        front_left_wheel  = carla.WheelPhysicsControl(tire_friction=2.0, damping_rate=1.5, max_steer_angle=70.0, long_stiff_value=1000)
        front_right_wheel = carla.WheelPhysicsControl(tire_friction=2.0, damping_rate=1.5, max_steer_angle=70.0, long_stiff_value=1000)
        rear_left_wheel   = carla.WheelPhysicsControl(tire_friction=3.0, damping_rate=1.5, max_steer_angle=0.0,  long_stiff_value=1000)
        rear_right_wheel  = carla.WheelPhysicsControl(tire_friction=3.0, damping_rate=1.5, max_steer_angle=0.0,  long_stiff_value=1000)

        wheels = [front_left_wheel, front_right_wheel, rear_left_wheel, rear_right_wheel]

        # Change Vehicle Physics Control parameters of the vehicle
        physics_control = actor.get_physics_control()

        physics_control.torque_curve = [carla.Vector2D(x=0, y=400), carla.Vector2D(x=1300, y=600)]
        physics_control.max_rpm = 10000
        physics_control.moi = 1.0
        physics_control.damping_rate_full_throttle = 0.0
        physics_control.use_gear_autobox = True
        physics_control.gear_switch_time = 0.5
        physics_control.clutch_strength = 10
        physics_control.mass = 10000
        physics_control.drag_coefficient = 0.25
        physics_control.steering_curve = [carla.Vector2D(x=0, y=1), carla.Vector2D(x=100, y=1), carla.Vector2D(x=300, y=1)]
        physics_control.use_sweep_wheel_collision = True
        physics_control.wheels = wheels

        # Apply Vehicle Physics Control for the vehicle
        actor.apply_physics_control(physics_control)
        print(physics_control)



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
            
    
    finally:
        print("Fechou")
        actor.destroy()

    
if __name__ == '__main__':

    main()
