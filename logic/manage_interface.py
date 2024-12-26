import pygame
from interfaces.advertising import Advertising
from interfaces.slot_machine import SlotMachine

class InterfaceManager:
    def __init__(self, screen):
        self.screen = screen  # Usar la pantalla existente
        self.clock = pygame.time.Clock()
        
        # Initialize interfaces
        self.advertising_interface = None
        self.slot_machine_interface = None
        self.initialize_interfaces()

    def initialize_interfaces(self):
        """Initialize or reinitialize the interfaces"""
        if self.advertising_interface is None:
            self.advertising_interface = Advertising()
        if self.slot_machine_interface is None:
            self.slot_machine_interface = SlotMachine()
        self.current_interface = self.advertising_interface

    def handle_command(self, command):
        """Handle command and switch interfaces accordingly."""
        if command == "1":
            if self.current_interface == self.slot_machine_interface:
                self.slot_machine_interface.stop()
                self.current_interface = None  # Asegurarse de que no hay interfaz activa
                self.advertising_interface = Advertising()
                self.current_interface = self.advertising_interface
                print("Switching to Advertising")
        elif command == "2":
            if self.current_interface == self.advertising_interface:
                self.advertising_interface.stop()
                pygame.time.wait(500)  # Esperar a que los recursos se liberen
                self.current_interface = None  # Asegurarse de que no hay interfaz activa
                self.slot_machine_interface = SlotMachine()
                self.current_interface = self.slot_machine_interface
                print("Switching to Slot Machine")

    def run(self):
        """Run the current interface."""
        if self.current_interface:
            self.screen.fill((0, 0, 0))
            self.current_interface.run(self.screen)
            pygame.display.flip()
            self.clock.tick(60)

    def stop(self):
        """Stop all interfaces and clean up."""
        if self.advertising_interface:
            self.advertising_interface.stop()
        if self.slot_machine_interface:
            self.slot_machine_interface.stop()
