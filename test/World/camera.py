import pygame
import carla
import numpy as np
import argparse

from pygame.locals import K_w
from pygame.locals import K_a
from pygame.locals import K_s
from pygame.locals import K_d
from pygame.locals import K_q
from pygame.locals import K_e



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

def  movement(pos_old):

    front = 0
    left = 0
    zoom = 0
    cameraPos = pos_old
    pressedButton =  pygame.key.get_pressed()
    if pressedButton[K_w]:
        front = 1
    elif pressedButton[K_s]:
        front = -1
    else:
        front = 0
                
                    
    if pressedButton[K_a]:
        left = -1
    elif pressedButton[K_d]:
        left = 1
    else:
        left = 0

    if pressedButton[K_q]:
        zoom = -1
    elif pressedButton[K_e]:
        zoom = 1
    else:
        zoom = 0
                
           
    cameraPos = carla.Transform(carla.Location(x = front, y=left, z = zoom) + cameraPos.location,cameraPos.rotation)

    return cameraPos


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

           # Initialise the camera floating behind the vehicle
        camera_init_trans = carla.Transform(carla.Location(x = 0, z=50), carla.Rotation(pitch=-90))
        camera_bp = world.get_blueprint_library().find('sensor.camera.rgb')
        #Tipo de objeto, position, filho de um objeto
        camera = world.spawn_actor(camera_bp, camera_init_trans)
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
            
            # Update the display
            gameDisplay.blit(renderObject.surface, (0,0))
            pygame.display.flip()
            # Process the current control state
            # Collect key press events
            camera.set_transform(movement(camera.get_transform()))
            world.tick()
            for event in pygame.event.get():
                # If the window is closed, break the while loop
                if event.type == pygame.QUIT:
                    crashed = True

        # Stop camera and quit PyGame after exiting game loop
        camera.stop()
        pygame.quit()   
      finally:
          print("Finalizou")


if __name__ in '__main__':
    main()


   