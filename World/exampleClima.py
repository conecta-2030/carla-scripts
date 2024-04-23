import carla
import argparse

def main():
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
    
    # Nomes Provisorio 
    argparser.add_argument(
        '--hour',
        metavar='HOUR',
        default=0.0,
        type=float,
        help='rate at which the weather changes (default: 1.0)')
    argparser.add_argument(
        '-i', '--intensidade',
        metavar='INTENSIDADE',
        default=0.0,
        type=float,
        help='rate at which the weather changes (default: 1.0)')
    args = argparser.parse_args()

    #Conecta com o Carla
    client = carla.Client(args.host, args.port)
    #Tempo de espera
    client.set_timeout(2.0)
    #Pego o mundo do Carla, para consegui acessar config dele
    world = client.get_world()

    #Pego a config do ambiente
    weather = world.get_weather()

    #
    weather.precipitation = args.intensidade

    weather.sun_altitude_angle = args.hour

    #Dou Valor do ambiente alterado para o mundo
    world.set_weather(weather)
  

if __name__ == '__main__':

    main()
