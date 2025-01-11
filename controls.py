import carla
import pygame

class DualControl:
    def __init__(self, world, start_in_autopilot):
        self._autopilot_enabled = start_in_autopilot
        self._control = carla.VehicleControl()
        self._lights = carla.VehicleLightState.NONE
        world.player.set_light_state(self._lights)
        world.player.set_autopilot(self._autopilot_enabled)
