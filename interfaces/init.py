# Clase principal que corre Pygame
import pygame
from server.server_socket import ServerSocket
from interfaces.advertising import Advertising
from interfaces.slot import Interface1

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((640, 480))
        self.clock = pygame.time.Clock()

        # Inicializar interfaces
        self.interface1 = Interface1()
        self.interface2 = Advertising()
        self.current_interface = self.interface1  # Empezar con la Interfaz 1

        # Iniciar servidor
        self.server = ServerSocket()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Revisar el comando recibido desde el servidor
            command = self.server.get_command()
            if command == "1":
                if self.current_interface == self.interface2:
                    self.interface2.stop()  # Stop the video
                self.current_interface = self.interface1
                print("Cambiando a Interface1")
            elif command == "2":
                if self.current_interface == self.interface1:
                    self.interface2 = Advertising()  # Reiniciar la interfaz publicitaria
                self.current_interface = self.interface2
                print("Cambiando a Advertising")

            # Mostrar la interfaz actual
            self.screen.fill((0, 0, 0))  # Limpiar la pantalla antes de dibujar la nueva interfaz
            self.current_interface.run(self.screen)  # Renderizar la interfaz actual
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
