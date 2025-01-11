import carla
import pygame
import math
try:
    import pygame
    from pygame.locals import KMOD_CTRL
    from pygame.locals import KMOD_SHIFT
    from pygame.locals import K_0
    from pygame.locals import K_9
    from pygame.locals import K_BACKQUOTE
    from pygame.locals import K_BACKSPACE
    from pygame.locals import K_COMMA
    from pygame.locals import K_DOWN
    from pygame.locals import K_ESCAPE
    from pygame.locals import K_F1
    from pygame.locals import K_LEFT
    from pygame.locals import K_PERIOD
    from pygame.locals import K_RIGHT
    from pygame.locals import K_SLASH
    from pygame.locals import K_SPACE
    from pygame.locals import K_TAB
    from pygame.locals import K_UP
    from pygame.locals import K_a
    from pygame.locals import K_c
    from pygame.locals import K_d
    from pygame.locals import K_h
    from pygame.locals import K_m
    from pygame.locals import K_p
    from pygame.locals import K_q
    from pygame.locals import K_r
    from pygame.locals import K_s
    from pygame.locals import K_w
except ImportError:
    raise RuntimeError('cannot import pygame, make sure pygame package is installed')



class DualControl:
    def __init__(self, world, start_in_autopilot):
        self._autopilot_enabled = start_in_autopilot
        self.world = world
        self._control = carla.VehicleControl()
        self._lights = carla.VehicleLightState.NONE

        # Set vehicle to autopilot if specified
        self.world.player.set_autopilot(self._autopilot_enabled)
        self.world.hud.notification("Press 'H' or '?' for help.", seconds=4.0)


    def parse_events(self, world, clock):
        if isinstance(self._control, carla.VehicleControl):
            current_lights = self._lights   #Aciona as Luzes
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    world.restart()
                elif event.button == 1:
                    world.hud.toggle_info()
                elif event.button == 2:
                    world.camera_manager.toggle_camera()
                elif event.button == 3:
                    world.next_weather()
                elif event.button == 12:
                    self._control.gear = 1
                elif event.button == 13:
                    self._control.gear = 2
                elif event.button == 14:
                    self._control.gear = 3
                elif event.button == 15:
                    self._control.gear = 4
                elif event.button == 16:
                    self._control.gear = 5
                elif event.button == 17:
                    self._control.gear = 6
                elif event.button == self._reverse_idx:
                    self._control.gear = -1
                elif event.button == 21:
                    world.camera_manager.move_x()

                elif event.button == 23:
                    world.camera_manager.next_sensor()
                elif event.button == 11 and pygame.key.get_mods() & KMOD_CTRL: # Representa "L"
                    current_lights ^= carla.VehicleLightState.Special1
                elif event.button == 11 and pygame.key.get_mods() & KMOD_SHIFT: # Representa "L"
                    current_lights ^= carla.VehicleLightState.HighBeam
                elif event.button == 11:
                    #print(event.button)

                    # Use 'L' key to switch between lights:
                    # closed -> position -> low beam -> fog
                    if not self._lights & carla.VehicleLightState.Position:
                        world.hud.notification("Position lights")
                        current_lights |= carla.VehicleLightState.Position
                    else:
                        world.hud.notification("Low beam lights")
                        current_lights |= carla.VehicleLightState.LowBeam
                    if self._lights & carla.VehicleLightState.LowBeam:
                        world.hud.notification("Fog lights")
                        current_lights |= carla.VehicleLightState.Fog
                    if self._lights & carla.VehicleLightState.Fog:
                        world.hud.notification("Lights off")
                        current_lights ^= carla.VehicleLightState.Position
                        current_lights ^= carla.VehicleLightState.LowBeam
                        current_lights ^= carla.VehicleLightState.Fog
                elif event.button == 10:
                    current_lights ^= carla.VehicleLightState.Interior
                elif event.button == 5:
                    current_lights ^= carla.VehicleLightState.LeftBlinker
                elif event.button == 4:
                    current_lights ^= carla.VehicleLightState.RightBlinker

            elif event.type == pygame.JOYBUTTONUP:
                if event.button in [12,13,14,15,16,17,18]: self._control.gear = 0

            elif event.type == pygame.KEYUP:
                if self._is_quit_shortcut(event.key):
                    return True
                elif event.key == K_BACKSPACE:
                    world.restart()
                elif event.key == K_F1:
                    world.hud.toggle_info()
                elif event.key == K_h or (event.key == K_SLASH and pygame.key.get_mods() & KMOD_SHIFT):
                    world.hud.help.toggle()
                elif event.key == K_TAB:
                    world.camera_manager.toggle_camera()
                elif event.key == K_c and pygame.key.get_mods() & KMOD_SHIFT:
                    world.next_weather(reverse=True)
                elif event.key == K_c:
                    world.next_weather()
                elif event.key == K_BACKQUOTE:
                    world.camera_manager.next_sensor()
                elif event.key > K_0 and event.key <= K_9:
                    world.camera_manager.set_sensor(event.key - 1 - K_0)
                elif event.key == K_r:
                    world.camera_manager.toggle_recording()
                if isinstance(self._control, carla.VehicleControl):
                    if event.key == K_q:
                        self._control.gear = 1 if self._control.reverse else -1
                    elif event.key == K_m:
                        self._control.manual_gear_shift = not self._control.manual_gear_shift
                        self._control.gear = world.player.get_control().gear
                        world.hud.notification('%s Transmission' %
                                               ('Manual' if self._control.manual_gear_shift else 'Automatic'))
                    elif self._control.manual_gear_shift and event.key == K_COMMA:
                        self._control.gear = max(-1, self._control.gear - 1)
                    elif self._control.manual_gear_shift and event.key == K_PERIOD:
                        self._control.gear = self._control.gear + 1 if self._control.gear < 6 else self._control.gear
                    elif event.key == K_p:
                        self._autopilot_enabled = not self._autopilot_enabled
                        world.player.set_autopilot(self._autopilot_enabled)
                        world.hud.notification('Autopilot %s' % ('On' if self._autopilot_enabled else 'Off'))

        if not self._autopilot_enabled:
            if isinstance(self._control, carla.VehicleControl):
                self._parse_vehicle_keys(pygame.key.get_pressed(), clock.get_time())
                #self._parse_vehicle_wheel()
                self._control.reverse = self._control.gear < 0

            #Linhas adicionais para acionar as luzes
            if self._control.brake:
                    current_lights |= carla.VehicleLightState.Brake
            else: # Remove the Brake flag
                    current_lights &= ~carla.VehicleLightState.Brake
            if self._control.reverse:
                    current_lights |= carla.VehicleLightState.Reverse
            else: # Remove the Reverse flag
                current_lights &= ~carla.VehicleLightState.Reverse
            if current_lights != self._lights: # Change the light state only if necessary
                    self._lights = current_lights
                    world.player.set_light_state(carla.VehicleLightState(self._lights))

            if current_lights != self._lights: # Change the light state only if necessary
                    self._lights = current_lights
                    world.player.set_light_state(carla.VehicleLightState(self._lights))

            elif isinstance(self._control, carla.WalkerControl):
                self._parse_walker_keys(pygame.key.get_pressed(), clock.get_time())
            world.player.apply_control(self._control)

    def _parse_vehicle_keys(self, keys, milliseconds):
        self._control.throttle = 1.0 if keys[K_UP] or keys[K_w] else 0.0
        steer_increment = 5e-4 * milliseconds
        if keys[K_LEFT] or keys[K_a]:
            self._steer_cache -= steer_increment
        elif keys[K_RIGHT] or keys[K_d]:
            self._steer_cache += steer_increment
        else:
            self._steer_cache = 0.0
        self._steer_cache = min(0.7, max(-0.7, self._steer_cache))
        self._control.steer = round(self._steer_cache, 1)
        self._control.brake = 1.0 if keys[K_DOWN] or keys[K_s] else 0.0
        self._control.hand_brake = keys[K_SPACE]

    

    @staticmethod
    def _is_quit_shortcut(key):
        """Check if the key combination is a quit shortcut."""
        return key == pygame.K_ESCAPE or (key == pygame.K_q and pygame.key.get_mods() & pygame.KMOD_CTRL)
