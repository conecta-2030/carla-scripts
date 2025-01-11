import random
import carla
from sensors import CollisionSensor, LaneInvasionSensor, GnssSensor
from camera_manager import CameraManager
from utils import get_actor_display_name
from weather_presets import WEATHER_PRESETS

class World:
    def __init__(self, carla_world, hud, actor_filter, weather_preset=None):
        self.world = carla_world
        self.hud = hud
        self.player = None
        self.collision_sensor = None
        self.lane_invasion_sensor = None
        self.gnss_sensor = None
        self.camera_manager = None
        self._weather_preset = weather_preset
        self._actor_filter = actor_filter
        self.restart(weather_preset)
        self.world.on_tick(hud.on_world_tick)

    def restart(self, weather_preset=None):
        cam_index = self.camera_manager.index if self.camera_manager is not None else 0
        cam_pos_index = self.camera_manager.transform_index if self.camera_manager is not None else 0
        blueprint = random.choice(self.world.get_blueprint_library().filter('vehicle.Jeep.Compass2023'))
        blueprint.set_attribute('role_name', 'hero')
        if blueprint.has_attribute('color'):
            color = random.choice(blueprint.get_attribute('color').recommended_values)
            blueprint.set_attribute('color', color)
        if self.player is not None:
            self.destroy()
        while self.player is None:
            spawn_points = self.world.get_map().get_spawn_points()
            spawn_point = random.choice(spawn_points) if spawn_points else carla.Transform()
            self.player = self.world.try_spawn_actor(blueprint, spawn_point)
        if weather_preset and weather_preset in WEATHER_PRESETS:
            self.world.set_weather(WEATHER_PRESETS[weather_preset])
        self.collision_sensor = CollisionSensor(self.player, self.hud)
        self.lane_invasion_sensor = LaneInvasionSensor(self.player, self.hud)
        self.gnss_sensor = GnssSensor(self.player)
        self.camera_manager = CameraManager(self.player, self.hud)
        self.camera_manager.transform_index = cam_pos_index
        self.camera_manager.set_sensor(cam_index, notify=False)
        actor_type = get_actor_display_name(self.player)
        self.hud.notification(actor_type)

    def tick(self, clock):
        self.hud.tick(self, clock)

    def render(self, display):
        self.camera_manager.render(display)

    def destroy(self):
        sensors = [
            self.camera_manager.sensor,
            self.collision_sensor.sensor,
            self.lane_invasion_sensor.sensor,
            self.gnss_sensor.sensor]
        for sensor in sensors:
            if sensor is not None:
                sensor.stop()
                sensor.destroy()
        if self.player is not None:
            self.player.destroy()
