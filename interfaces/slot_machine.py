import pygame

# Interfaz 1 - Bienvenida
class Interface1:
    def run(self, screen):
        font = pygame.font.SysFont('Arial', 36)
        text = font.render("Bienvenido a la interfaz 1!", True, (255, 255, 255))
        screen.fill((0, 0, 0))  # Fondo negro
        screen.blit(text, (150, 200))

import pygame
import random
import sys

from data.data_base import DataBase
from data.internal_data import InternalData

from assets.config import (
    AQUAMARINE,
    ORANGE_NEON,
    PADDING,
    CHARTREUSE,
    LINE_WIDHT,
    COOL_GRAY_LIGHT,
    COOL_GRAY_DARK,
    FPS,
    BLACK,
    SLOT_MACHINE_AUDIO_PATH,
    SLOT_MACHINE_FONT_PATH,
    SLOT_MACHINE_IMAGE_PATH
)


class SlotMachine:
    """
    Slot machine game class that manages the game screen, slot animations,
    user input, and display of win/loss messages. It handles setting up the
    Pygame environment, drawing game elements, and managing game states.
    """

    def __init__(self) -> None:
        """
        Initializes the Game instance by setting up the screen, loading images,
        and configuring essential game settings such as display dimensions,
        gradient backgrounds, and sound effects. Also initializes the joystick
        if detected.
        """

        # Acces Data
        self.shared_data = DataBase()
        self.internal_data = InternalData()

        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.WIDTH, self.HEIGHT = self.screen.get_width(), self.screen.get_height()
        pygame.display.set_caption("Slot machine game")
        self.icon = pygame.image.load(f"{SLOT_MACHINE_IMAGE_PATH}icon_plant.png")
        pygame.display.set_icon(self.icon)
        pygame.mouse.set_visible(False)
        self.clock = pygame.time.Clock()

        self.delta_time: int = 0

        # Set up gradient background
        self.gradient_surface = pygame.Surface((self.WIDTH, self.HEIGHT))
        self.draw_gradient_surface(
            self.gradient_surface, AQUAMARINE, ORANGE_NEON, self.WIDTH, self.HEIGHT
        )

        self.frame_thickness: int = 60

        # Calculate slot cell dimensions
        self.cell_width = (self.WIDTH - 2 * PADDING - 2 * self.frame_thickness) // 3
        self.cell_height = self.HEIGHT - 2 * PADDING - 2 * self.frame_thickness

        self.border_radius: int = 15

        # Load slot images for regular animation
        self.slot_regular_images = [
            pygame.image.load(f"{SLOT_MACHINE_IMAGE_PATH}image{i}.png").convert_alpha()
            for i in range(1, 8)
        ]

        # Load slot images for winner animation
        self.slot_winner_images = [
            pygame.image.load(f"{SLOT_MACHINE_IMAGE_PATH}image{i}.png").convert_alpha()
            for i in range(1, 9)
        ]

        # change of images
        self.slot_images = self.slot_regular_images

        # Initialize slot display settings
        self.slots = [0, 0, 0]

        # Acces counter data
        self.spin_count = self.internal_data.get_counter()

        # Set up gradient surfaces for each slot
        self.slot_gradients = [
            pygame.Surface((self.cell_width, self.cell_height), pygame.SRCALPHA)
            for _ in range(3)
        ]
        for slot_surface in self.slot_gradients:
            self.draw_gradient_surface(
                slot_surface, ORANGE_NEON, CHARTREUSE, self.cell_width, self.cell_height
            )

        # Load decorative images and resize
        self.decoration_images = [
            pygame.image.load(f"{SLOT_MACHINE_IMAGE_PATH}deco{i}.png").convert_alpha()
            for i in range(1, 5)
        ]
        self.decoration_size = (100, 100)
        self.decoration_images = [
            pygame.transform.scale(img, self.decoration_size)
            for img in self.decoration_images
        ]

        # Load sounds for win and lose outcomes
        self.winner_sound = pygame.mixer.Sound(f"{SLOT_MACHINE_AUDIO_PATH}win.mp3")
        self.lose_sound = pygame.mixer.Sound(f"{SLOT_MACHINE_AUDIO_PATH}lose.mp3")

        # Configure win message properties
        self.show_winner_message: bool = False
        self.winner_message_font_size: int = 150
        self.winner_message_rect_padding: int = 20
        self.winner_message_border_thickeness: int = 19
        self.winner_message_border_radius: int = 20

        # Configure additional display duration for win message
        self.additional_display_time = 4000

        # Configure loss message properties
        self.show_loss_message: bool = False
        self.loss_message_font_size: int = 70
        self.loss_message_rect_padding: int = 20
        self.loss_message_border_thickeness: int = 5
        self.loss_message_border_radius: int = 20

        self.font_path: str = f"{SLOT_MACHINE_FONT_PATH}HackNerdFont-BoldItalic.ttf"

        # Initialize joystick if available
        self.init_joystick()

    def init_joystick(self) -> None:
        """Initialize the joyshtick and verifies if are one"""
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            print(f"Joystick connected: {self.joystick.get_name()}")
        else:
            print("No joystick detected.")

    def get_state(self) -> str:
        """
        Retrieves the current state of the button from the shared DataBase.

        Returns:
            bool: The active state of the button.
        """
        button_state = self.shared_data.get_value_state("active_button")
        return button_state

    def is_winner_attemp(self) -> bool:
        """
        Checks if the current spin count indicates a winning attempt.

        Returns:
            bool: True if spin count is a multiple of 5, indicating a winning attempt.
        """
        if self.spin_count:
            return self.spin_count % 5 == 0
        else:
            return False

    def draw_gradient_surface(
        self,
        surface: pygame.Surface,
        color_top: tuple[int, int, int],
        color_bottom: tuple[int, int, int],
        width: int,
        height: int,
    ) -> None:
        """
        Draws a gradient on a given surface transitioning from color_top to
        color_bottom vertically.

        Args:
            surface (pygame.Surface): Surface on which the gradient is drawn.
            color_top (tuple): RGB color at the top of the gradient.
            color_bottom (tuple): RGB color at the bottom of the gradient.
            width (int): Width of the gradient surface.
            height (int): Height of the gradient surface.
        """
        for i in range(height):
            color = (
                color_top[0] + (color_bottom[0] - color_top[0]) * i / height,
                color_top[1] + (color_bottom[1] - color_top[1]) * i / height,
                color_top[2] + (color_bottom[2] - color_top[2]) * i / height,
            )
            pygame.draw.line(surface, color, (0, i), (width, i))

    def draw_grid(self) -> None:
        """
        Draws the main slot machine grid and decorative frame on the game screen.
        It includes the three slot cells with gradient backgrounds and a frame
        surrounding the grid. Adds decorative rotated images to each corner.
        """
        total_width = 3 * self.cell_width
        total_height = self.cell_height
        grid_x = (self.WIDTH - total_width) // 2
        grid_y = (self.HEIGHT - total_height) // 2

        for col in range(3):
            x = grid_x + col * self.cell_width
            y = grid_y
            cell_bg_rect = (x, y, self.cell_width, self.cell_height)

            # Set and reset clipping area for gradient drawing
            clip_rect = pygame.Rect(x, y, self.cell_width, self.cell_height)
            self.screen.set_clip(clip_rect)
            self.screen.blit(self.slot_gradients[col], (x, y))
            self.screen.set_clip(None)

            # Draw cell border
            pygame.draw.rect(
                self.screen,
                COOL_GRAY_LIGHT,
                cell_bg_rect,
                LINE_WIDHT,
                border_radius=self.border_radius,
            )

        # Draw grid frame
        frame_rect = (
            grid_x - self.frame_thickness,
            grid_y - self.frame_thickness,
            total_width + 2 * self.frame_thickness,
            total_height + 2 * self.frame_thickness,
        )
        pygame.draw.rect(
            self.screen,
            COOL_GRAY_DARK,
            frame_rect,
            self.frame_thickness,
            border_radius=self.border_radius - 5,
        )

        # Define decorative image placement and rotation
        corners = [
            (grid_x - 50, grid_y - 50),
            (grid_x + total_width - 50, grid_y - 50),
            (grid_x - 50, grid_y + total_height - 100),
            (grid_x + total_width - 50, grid_y + total_height - 100),
        ]
        rotation_angles = [45, -45, 45, -45]

        for corner, angle, image in zip(
            corners, rotation_angles, self.decoration_images
        ):
            rotated_image = pygame.transform.rotate(image, angle)
            image_rect = rotated_image.get_rect(topleft=corner)
            self.screen.blit(rotated_image, image_rect.topleft)

    def draw_slots(self) -> None:
        """
        Draws each slot on the screen with its assigned image, scaled to fit
        within the slot cell dimensions.
        """
        for i in range(3):
            # Calculate the position of each slot based on screen and cell dimensions
            x = (self.WIDTH - 3 * self.cell_width) // 2 + i * self.cell_width
            y = (self.HEIGHT - self.cell_height) // 2

            # Resize the slot image for consistent visual appearance
            reduced_size = (250, 250)
            slot_image = pygame.transform.scale(
                self.slot_winner_images[self.slots[i]], reduced_size
            )

            # Center the slot image in its designated slot area
            image_rect = slot_image.get_rect(
                center=(x + self.cell_width // 2, y + self.cell_height // 2)
            )
            self.screen.blit(slot_image, image_rect.topleft)

    def display_message(
        self,
        state_message: bool,
        font_size: int,
        padding: int,
        border_thickness: int,
        border_radius: int,
        font_color: tuple[int, int, int],
        outside_border_color: tuple[int, int, int],
        background_color: tuple[int, int, int],
        inside_border_color: tuple[int, int, int],
        message: str,
    ) -> None:
        """
        Displays a centered message with decorative borders on the screen if a specified condition is met.

        Args:
        ----------
            state_message : bool
                If True, the message will be displayed; if False, no message is shown.
            font_size : int
                The font size for the message text.
            padding : int
                The padding between the text and the background rectangle.
            border_thickness : int
                The thickness of the inner border around the text.
            border_radius : int
                The radius for rounding the corners of the background and borders.
            font_color : tuple
                The RGB color of the text font.
            outside_border_color : tuple
                The RGB color of the outer border surrounding the message box.
            background_color : tuple
                The RGB color of the message background.
            inside_border_color : tuple
                The RGB color of the inner border around the text.
            message : str
                The message to be displayed.
        """
        if state_message:
            # Create font and render winner text
            font = pygame.font.Font(self.font_path, font_size)
            winner_text = font.render(message, True, font_color)
            text_rect = winner_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))

            # Calculate rectangle dimensions for text background and border
            rect_width = text_rect.width + 2 * padding
            rect_height = text_rect.height + 2 * padding
            rect_x = text_rect.centerx - rect_width // 2
            rect_y = text_rect.centery - rect_height // 2
            rect = pygame.Rect(rect_x, rect_y, rect_width, rect_height)

            # Define and draw the outer border rectangle
            border_rect = pygame.Rect(
                rect_x - border_thickness,
                rect_y - border_thickness,
                rect_width + 2 * border_thickness,
                rect_height + 2 * border_thickness,
            )
            pygame.draw.rect(
                self.screen,
                outside_border_color,
                border_rect,
                0,
                border_radius + 5,
            )

            # Draw the inner rectangles with the message and borders
            pygame.draw.rect(self.screen, background_color, rect, 0, border_radius)

            pygame.draw.rect(
                self.screen,
                inside_border_color,
                rect,
                border_thickness,
                border_radius,
            )

            # Display winner text
            self.screen.blit(winner_text, text_rect.topleft)

    def change_colors(
        self, color_top: tuple[int, int, int], color_bottom: tuple[int, int, int]
    ) -> None:
        """
        Updates the gradient colors for each slot surface.

        Args:
            color_top: The top color of the gradient.
            color_bottom: The bottom color of the gradient.
        """
        for slot_surface in self.slot_gradients:
            self.draw_gradient_surface(
                slot_surface, color_top, color_bottom, self.cell_width, self.cell_height
            )

    def spin_slots(self) -> None:
        """
        Initiates the slot spinning animation with varied spin times for each slot.
        Determines the result of the spin, displaying a win or loss message based
        on the outcome.
        """

        self.slot_images = self.slot_regular_images
        # Set random spin times for each slot
        spin_time = [random.randint(3000, 5000) for _ in range(3)]
        start_time = [
            pygame.time.get_ticks() + random.randint(0, 500) for _ in range(3)
        ]
        end_time = [st + spin for st, spin in zip(start_time, spin_time)]
        finished_slots = [False] * 3
        running = True

        # Update gradient colors and initiate the spin process
        self.change_colors(ORANGE_NEON, CHARTREUSE)
        self.draw_gradient_surface(
            self.gradient_surface, AQUAMARINE, ORANGE_NEON, self.WIDTH, self.HEIGHT
        )
        self.shared_data.set_value_game_state("state", "PROCESANDO...")

        # Spin loop, checking if all slots have finished spinning
        while running:
            current_time = pygame.time.get_ticks()
            running = False
            for i in range(3):
                if current_time < end_time[i]:
                    running = True
                    self.slots[i] = (self.slots[i] + 1) % len(self.slot_images)
                else:
                    finished_slots[i] = True

            # Check for quit event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Refresh display
            self.screen.blit(self.gradient_surface, (0, 0))
            self.draw_grid()
            self.draw_slots()
            pygame.display.flip()
            self.clock.tick(FPS // 5)

        # Determine outcome: win or loss
        if self.is_winner_attemp():
            self.slot_images = self.slot_winner_images
            self.spin_to_winner()
            pygame.time.delay(1000)
            self.change_colors(CHARTREUSE, AQUAMARINE)
            self.winner_sound.play()
            self.show_winner_message = True
            # Prueba para minimizar código
            self.show_loss_message = False
            pygame.time.set_timer(
                pygame.USEREVENT,
                int(self.winner_sound.get_length() * 1000)
                + self.additional_display_time,
            )
            self.internal_data.set_env_variable("COUNTER", "1")
            self.shared_data.set_value_game_state("state", "GANADOR")
        else:
            self.slot_images = self.slot_regular_images
            self.stop_slots(finished_slots)
            # self.ensure_no_winner()
            pygame.time.delay(1000)
            self.draw_gradient_surface(
                self.gradient_surface, ORANGE_NEON, ORANGE_NEON, self.WIDTH, self.HEIGHT
            )
            self.lose_sound.play()
            self.show_loss_message = True
            self.show_winner_message = False
            pygame.time.set_timer(pygame.USEREVENT, self.additional_display_time + 3500)
            self.shared_data.set_value_game_state("state", "PERDEDOR")

        # Display final result
        self.display_final_result()

    def spin_to_winner(self) -> None:
        """
        Adjusts slot positions to align them with the winning frame.
        """
        winner_frame = 7
        steps_needed = [
            (winner_frame - slot) % len(self.slot_winner_images) for slot in self.slots
        ]

        # Spin slots to their winning positions
        running = True
        while running:
            running = False
            for i in range(3):
                if steps_needed[i] > 0:
                    running = True
                    self.slots[i] = (self.slots[i] + 1) % len(self.slot_winner_images)
                    steps_needed[i] -= 1

            # Check for quit event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Refresh display
            self.screen.blit(self.gradient_surface, (0, 0))
            self.draw_grid()
            self.draw_slots()
            pygame.display.flip()
            self.clock.tick(FPS // 5)

        self.slot_images = self.slot_regular_images

    def stop_slots(self, finished_slots: list[bool]) -> None:
        """
        Stops the slots that are not finished, setting each slot to a randomly
        generated "winner" symbol. If the winning condition is not met, ensures
        that there is no accidental winner.

        Args:
            finished_slots (list of bool): List indicating which slots have finished.

        Returns:
            list: Current slot values after stopping.
        """
        # Generate a random winning symbol for each slot that is not finished
        winners = [
            random.randint(0, len(self.slot_regular_images) - 1) for _ in range(3)
        ]
        for i in range(3):
            if not finished_slots[i]:
                # Set slot to winner if it hasn't finished spinning
                self.slots[i] = winners[i]

    def display_final_result(self) -> None:
        """
        Displays the final result of each slot from right to left with a delay,
        emphasizing the last slot.
        """
        # Display each slot's result with a delay, starting from the last
        for i in reversed(range(3)):
            slot_end_time = pygame.time.get_ticks() + (3 - i) * 500
            while pygame.time.get_ticks() < slot_end_time:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        # Quit the game on close event
                        pygame.quit()
                        sys.exit()

                # Redraw the screen and display the current slot results
                self.screen.blit(self.gradient_surface, (0, 0))
                self.draw_grid()
                self.draw_slots()
                pygame.display.flip()
                self.clock.tick(FPS)

    def stop(self) -> None:
        """
        Stops the game by stopping the winner sound, clearing the screen,
        and quitting the Pygame session.
        """
        # Stop winner sound if playing
        self.winner_sound.stop()
        self.lose_sound.stop()
        self.running = False

        # Clear the screen and update display
        self.screen.fill(BLACK)
        pygame.display.flip()

        # Quit Pygame and exit program
        pygame.quit()
        sys.exit()

    def display_final_message(self) -> None:
        # winner message
        self.display_message(
            self.show_winner_message,
            self.winner_message_font_size,
            self.winner_message_rect_padding,
            self.winner_message_border_thickeness,
            self.winner_message_border_radius,
            COOL_GRAY_LIGHT,
            CHARTREUSE,
            ORANGE_NEON,
            COOL_GRAY_LIGHT,
            "¡ GANADOR !",
        )

        # loss message
        self.display_message(
            self.show_loss_message,
            self.loss_message_font_size,
            self.loss_message_rect_padding,
            self.loss_message_border_thickeness,
            self.loss_message_border_radius,
            ORANGE_NEON,
            COOL_GRAY_DARK,
            COOL_GRAY_LIGHT,
            CHARTREUSE,
            "¡ Suerte la Próxima !",
        )

    def run(self) -> None:
        # Initialize start time and load spin counter from file
        self.start_time = pygame.time.get_ticks()
        running = True
        counter = self.internal_data.get_counter()

        while running:
            for event in pygame.event.get():
                state_button = self.get_state()
                if event.type == pygame.QUIT:
                    # End game loop on quit event
                    running = False
                if state_button == "True":
                    if event.type == pygame.JOYBUTTONDOWN:
                        if event.button == 0:
                            # Update and save spin counter on button press
                            self.spin_count = counter = (
                                self.internal_data.get_counter()
                            )
                            counter += 1
                            self.internal_data.set_env_variable("COUNTER", f"{counter}")
                            self.spin_slots()
                            # Set button state to inactive after spin
                            self.shared_data.set_value_state("active_button", "False")

                if event.type == pygame.USEREVENT:
                    # Hide winner and loss messages after display time ends
                    self.show_winner_message = False
                    self.show_loss_message = False

            # Wait briefly to prevent excessive CPU usage
            pygame.time.wait(100)

            self.draw_gradient_surface(
                self.gradient_surface, AQUAMARINE, ORANGE_NEON, self.WIDTH, self.HEIGHT
            )
            # Update time delta and render background, grid, and slots
            self.delta_time = (pygame.time.get_ticks() - self.start_time) / 1000
            self.screen.blit(self.gradient_surface, (0, 0))
            self.draw_grid()
            self.draw_slots()
            self.display_final_message()
            pygame.display.update()
            self.clock.tick(FPS)

if __name__ == "__main__":
    slot_machine = SlotMachine()
    slot_machine.run()
