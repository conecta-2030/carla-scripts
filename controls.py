import carla
import pygame
import math

class DualControl:
    def __init__(self, world, start_in_autopilot):
        self._autopilot_enabled = start_in_autopilot
        self.world = world
        self._control = carla.VehicleControl()
        self._steer_cache = 0.0

        # Enable autopilot for the vehicle if specified
        self.world.player.set_autopilot(self._autopilot_enabled)

        # Notification for controls
        self.world.hud.notification("Press 'H' or '?' for help.", seconds=4.0)

    def parse_events(self, world, clock):
        """Parse keyboard events for controlling the vehicle."""
        keys = pygame.key.get_pressed()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            elif event.type == pygame.KEYUP:
                if self._is_quit_shortcut(event.key):
                    return True
                elif event.key == pygame.K_BACKSPACE:
                    world.restart()
                elif event.key == pygame.K_h or (event.key == pygame.K_SLASH and pygame.key.get_mods() & pygame.KMOD_SHIFT):
                    world.hud.help.toggle()
                elif event.key == pygame.K_TAB:
                    world.camera_manager.toggle_camera()
                elif event.key == pygame.K_r:
                    world.camera_manager.toggle_recording()
                elif event.key == pygame.K_p:
                    self._autopilot_enabled = not self._autopilot_enabled
                    world.player.set_autopilot(self._autopilot_enabled)
                    world.hud.notification(f"Autopilot {'On' if self._autopilot_enabled else 'Off'}")

        if not self._autopilot_enabled:
            self._parse_vehicle_keys(keys, clock.get_time())
            self._control.reverse = self._control.gear < 0
            world.player.apply_control(self._control)

        return False

    def _parse_vehicle_keys(self, keys, milliseconds):
        """Parse keyboard input for vehicle control."""
        self._control.throttle = 1.0 if keys[pygame.K_UP] or keys[pygame.K_w] else 0.0
        steer_increment = 5e-4 * milliseconds
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self._steer_cache -= steer_increment
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self._steer_cache += steer_increment
        else:
            self._steer_cache = 0.0
        self._steer_cache = min(0.7, max(-0.7, self._steer_cache))
        self._control.steer = round(self._steer_cache, 1)
        self._control.brake = 1.0 if keys[pygame.K_DOWN] or keys[pygame.K_s] else 0.0
        self._control.hand_brake = keys[pygame.K_SPACE]

    @staticmethod
    def _is_quit_shortcut(key):
        """Check if the key combination is a quit shortcut."""
        return key == pygame.K_ESCAPE or (key == pygame.K_q and pygame.key.get_mods() & pygame.KMOD_CTRL)
