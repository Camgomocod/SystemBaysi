import pygame
import sys
from assets.config import (
    INIT_IMAGE_PATH,
    AQUAMARINE,
    CHARTREUSE,
    ORANGE_NEON,
)
from data.data_base import DataBase
from data.internal_data import InternalData
from server.server_socket import ServerSocket
from logic.manage_interface import InterfaceManager

class Init:
    """Class to initialize the application and handle the initial interface."""

    def __init__(self) -> None:
        """Initialize Pygame, set up the display, and initialize components."""
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.screen_width, self.screen_height = self.screen.get_size()
        
        self.internal_data = InternalData()
        self.shared_data = DataBase()
        self.running = True
        self.first_command_received = False
        self.connection_established = False

        # Initialize the socket and interface manager with the existing screen
        self.socket_client = ServerSocket()
        self.interface_manager = InterfaceManager(self.screen)
        
        # Register callbacks for commands
        self.register_command_handlers()
        
        self.last_game_state = None
        
        # Setup Pygame window
        self.setup_pygame_window()
        
        # Create gradient surface for the entire screen
        self.gradient_surface = pygame.Surface((self.screen_width, self.screen_height))

        # Update connection state after initializing the socket
        self.update_connection_state()

    def update_connection_state(self) -> None:
        """Update the connection state from the socket."""
        self.connection_established = self.socket_client.connection_established
        if not self.connection_established:
            print("Waiting for server connection...")

    def register_command_handlers(self) -> None:
        """Register command handlers for the server commands."""
        self.socket_client.register_callback("sorteo", self.handle_sorteo)
        self.socket_client.register_callback("publicidad", self.handle_publicidad)
        self.socket_client.register_callback("button", self.handle_button)
        self.socket_client.register_callback("salir", self.handle_salir)

    def handle_sorteo(self) -> None:
        """Handle the 'sorteo' command."""
        self.first_command_received = True
        self.interface_manager.switch_to_slot_machine()
        self.interface_manager.run()

    def handle_publicidad(self) -> None:
        """Handle the 'publicidad' command."""
        self.first_command_received = True
        self.interface_manager.switch_to_advertising()
        self.interface_manager.run()

    def handle_button(self) -> None:
        """Handle the 'button' command."""
        pass  # Implement if necessary

    def handle_salir(self) -> None:
        """Handle the 'salir' command."""
        self.interface_manager.stop()
        self.stop()

    def setup_pygame_window(self) -> None:
        """Set up Pygame window elements."""
        # Adjust the logo size proportionally to the screen
        self.size_logo = (int(self.screen_width * 0.15), int(self.screen_height * 0.15))
        
        pygame.display.set_caption("BAYSI")
        self.icon = pygame.image.load(f"{INIT_IMAGE_PATH}icon_plant.png")
        pygame.display.set_icon(self.icon)

        self.logo = pygame.image.load(f"{INIT_IMAGE_PATH}logo.png")
        self.logo = pygame.transform.scale(self.logo, self.size_logo)
        self.logo_rect = self.logo.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2)
        )

        # Adjust UI element sizes proportionally
        self.button_size = int(self.screen_width * 0.03)
        self.button_rect = pygame.Rect(
            self.screen_width * 0.05, 
            self.screen_height * 0.05, 
            self.button_size, 
            self.button_size
        )

        self.label_width = int(self.screen_width * 0.2)
        self.label_height = int(self.screen_height * 0.04)
        self.label_rect = pygame.Rect(
            self.button_rect.right + 10,
            self.button_rect.y,
            self.label_width,
            self.label_height
        )

        # Adjust font size
        self.small_font = pygame.font.Font(None, int(self.screen_height * 0.03))
        
        self.label_active = False
        self.input_text = ""
        self.place_holder_text = "Enter new IP"

        # Load and scale the settings icon
        self.gear_icon = pygame.image.load(f"{INIT_IMAGE_PATH}setting.png")
        self.gear_icon = pygame.transform.scale(
            self.gear_icon,
            (int(self.button_size * 0.8), int(self.button_size * 0.8))
        )

    def get_game_state(self) -> str:
        """
        Get the current game state.

        Returns:
            str: The current game state.
        """
        return self.shared_data.get_value_game_state("state")

    def send_command(self, command: str) -> None:
        """
        Send a command to the server.

        Args:
            command (str): The command to send.
        """
        self.socket_client.send_command(command)

    def stop(self) -> None:
        """Stop the application and clean up resources."""
        self.running = False
        self.socket_client.stop()
        pygame.quit()
        sys.exit()

    def run(self) -> None:
        """Main method to start the application."""
        self.show_initial_screen()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Check the command received from the server
            command = self.socket_client.get_command()
            if command:
                self.interface_manager.handle_command(command)
                self.interface_manager.run()

            pygame.time.wait(100)

        self.stop()

    def draw_gradient_surface(self, top_color: tuple[int, int, int], bottom_color: tuple[int, int, int]) -> None:
        """
        Draw a gradient on the entire screen.

        Args:
            top_color (tuple[int, int, int]): The top color of the gradient.
            bottom_color (tuple[int, int, int]): The bottom color of the gradient.
        """
        for i in range(self.screen_height):
            color = (
                int(
                    top_color[0]
                    + (bottom_color[0] - top_color[0]) * i / self.screen_height
                ),
                int(
                    top_color[1]
                    + (bottom_color[1] - top_color[1]) * i / self.screen_height
                ),
                int(
                    top_color[2]
                    + (bottom_color[2] - top_color[2]) * i / self.screen_height
                ),
            )
            pygame.draw.line(
                self.gradient_surface, color, (0, i), (self.screen_width, i)
            )

    def show_initial_screen(self) -> None:
        """Show the initial screen in full screen mode."""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop()

            # Update the connection state before drawing
            self.update_connection_state()
            
            # Draw directly on the full screen
            if self.connection_established:
                self.draw_gradient_surface(CHARTREUSE, AQUAMARINE)
            else:
                self.draw_gradient_surface(AQUAMARINE, ORANGE_NEON)

            self.screen.blit(self.gradient_surface, (0, 0))
            self.screen.blit(self.logo, self.logo_rect)
            pygame.display.flip()

            command = self.socket_client.get_command()
            if command:
                self.interface_manager.handle_command(command)
                break

        self.interface_manager.run()