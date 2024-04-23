import carla
import argparse
import random
import pygame
import numpy as np



def spawn_ai(world,pedestrians,spawnPoints):

    spawned_ai_walkers = []

    for number in range(0,len(pedestrians)):
        
        pedestrian_bp = pedestrians[number]

        aiWalker = world.get_blueprint_library().find('controller.ai.walker')
        aiActor = world.spawn_actor(aiWalker,spawnPoints[number],pedestrian_bp)
        spawned_ai_walkers.append(aiActor)

    return spawned_ai_walkers

def spawn_walker(world, spawnPoints):
    spawned_pedestrians = []

    for spawn_point in spawnPoints:
        
        pedestrian_bp = random.choice(world.get_blueprint_library().filter('walker.pedestrian.*'))
        pedestrian = world.spawn_actor(pedestrian_bp,spawn_point) 
        spawned_pedestrians.append(pedestrian)

    return spawned_pedestrians


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
        world.set_pedestrians_cross_factor(0.5)
        spawn_points = world.get_map().get_spawn_points()
        
        random.shuffle(spawn_points)
        spawn_points = spawn_points[:20]
        pedestrians = spawn_walker(world,spawn_points)
        aiWalkers = spawn_ai(world,pedestrians,spawn_points)

        for walker in aiWalkers:
            walker.start()
            walker.go_to_location(world.get_random_location_from_navigation())
            walker.set_max_speed(1+random.random())

         # Initialise the camera floating behind the vehicle
        camera_init_trans = carla.Transform(carla.Location(x = -2, z=2), carla.Rotation(pitch=-45))
        camera_bp = world.get_blueprint_library().find('sensor.camera.rgb')
        #Tipo de objeto, position, filho de um objeto
        camera = world.spawn_actor(camera_bp, camera_init_trans, attach_to=pedestrians[0])
        print(pedestrians[0])
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
        print("fechou sessao")
        camera_bp.destroy()
        camera.stop()
        pygame.quit() 
        for walker in pedestrians:
            walker.destroy()
        for ai in aiWalkers:
            ai.destroy()




if __name__ == '__main__':
    main()