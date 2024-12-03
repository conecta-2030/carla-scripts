import carla

WEATHER_PRESETS = {
    "rain": carla.WeatherParameters(
        cloudiness=100.0,
        precipitation=100.0,
        precipitation_deposits=100.0,
        wind_intensity=50.0,
        sun_azimuth_angle=45.0,
        sun_altitude_angle=10.0
    ),
    "sun": carla.WeatherParameters(
        cloudiness=10.0,
        precipitation=0.0,
        precipitation_deposits=0.0,
        wind_intensity=5.0,
        sun_azimuth_angle=120.0,
        sun_altitude_angle=90.0
    ),
    "night": carla.WeatherParameters(
        cloudiness=20.0,
        precipitation=0.0,
        precipitation_deposits=0.0,
        wind_intensity=5.0,
        sun_azimuth_angle=45.0,
        sun_altitude_angle=-20.0
    ),
    "fog": carla.WeatherParameters(
        cloudiness=60.0,
        precipitation=0.0,
        precipitation_deposits=0.0,
        wind_intensity=5.0,
        sun_azimuth_angle=120.0,
        sun_altitude_angle=50.0,
        fog_density=80.0,
        fog_distance=10.0,
        wetness=30.0
    )
}