# Main class that runs Pygame
import pygame
from server.server_socket import ServerSocket
from interfaces.advertising import Advertising
from interfaces.slot_machine import Interface1
from interfaces.slot_machine import SlotMachine

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((640, 480))
        self.clock = pygame.time.Clock()

        # Initialize interfaces
        self.interface1 = Interface1()
        self.interface2 = Advertising()
        self.current_interface = self.interface1  # Start with Interface 1

        # Start server
        self.server = ServerSocket()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Check the command received from the server
            command = self.server.get_command()
            if command == "1":
                if self.current_interface == self.interface2:
                    self.interface2.stop()  # Stop the video
                self.current_interface = self.interface1
                print("Switching to Interface1")
            elif command == "2":
                if self.current_interface == self.interface1:
                    self.interface2 = Advertising()  # Restart the advertising interface
                self.current_interface = self.interface2
                print("Switching to Advertising")

            # Display the current interface
            self.screen.fill((0, 0, 0))  # Clear the screen before drawing the new interface
            self.current_interface.run(self.screen)  # Render the current interface
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
    
    def run_slot(self):
        slot_machine = SlotMachine()
        slot_machine.run()
