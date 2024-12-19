# Main class that runs Pygame
import pygame
from server.server_socket import ServerSocket
from interfaces.advertising import Advertising
from interfaces.slot_machine import SlotMachine

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()

        # Initialize interfaces
        self.advertising_interface = None
        self.slot_machine_interface = None
        self.initialize_interfaces()
        
        # Start server
        self.server = ServerSocket()

    def initialize_interfaces(self):
        """Initialize or reinitialize the interfaces"""
        if self.advertising_interface is None:
            self.advertising_interface = Advertising()
        if self.slot_machine_interface is None:
            self.slot_machine_interface = SlotMachine()
        self.current_interface = self.advertising_interface

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Check the command received from the server
            command = self.server.get_command()
            if command == "1":
                if self.current_interface == self.slot_machine_interface:
                    self.slot_machine_interface.stop()
                    self.advertising_interface = Advertising()  # Reinitialize advertising
                self.current_interface = self.advertising_interface
                print("Switching to Advertising")
            elif command == "2":
                if self.current_interface == self.advertising_interface:
                    self.advertising_interface.stop()
                    self.slot_machine_interface = SlotMachine()  # Reinitialize slot machine
                self.current_interface = self.slot_machine_interface
                print("Switching to Slot Machine")

            # Display the current interface
            self.screen.fill((0, 0, 0))
            self.current_interface.run(self.screen)
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
