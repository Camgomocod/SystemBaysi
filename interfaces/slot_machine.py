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
    """Class to handle slot machine game interface."""

    def __init__(self) -> None:
        """Initialize Pygame, set up the display, and load game assets."""
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

        self.gradient_surface = pygame.Surface((self.WIDTH, self.HEIGHT))
        self.draw_gradient_surface(
            self.gradient_surface, AQUAMARINE, ORANGE_NEON, self.WIDTH, self.HEIGHT
        )

        self.frame_thickness: int = 60

        self.cell_width = (self.WIDTH - 2 * PADDING - 2 * self.frame_thickness) // 3
        self.cell_height = self.HEIGHT - 2 * PADDING - 2 * self.frame_thickness

        self.border_radius: int = 15

        self.slot_regular_images = [
            pygame.image.load(f"{SLOT_MACHINE_IMAGE_PATH}image{i}.png").convert_alpha()
            for i in range(1, 8)
        ]

        self.slot_winner_images = [
            pygame.image.load(f"{SLOT_MACHINE_IMAGE_PATH}image{i}.png").convert_alpha()
            for i in range(1, 9)
        ]

        self.slot_images = self.slot_regular_images

        self.slots = [0, 0, 0]

        self.spin_count = self.internal_data.get_counter()

        self.slot_gradients = [
            pygame.Surface((self.cell_width, self.cell_height), pygame.SRCALPHA)
            for _ in range(3)
        ]
        for slot_surface in self.slot_gradients:
            self.draw_gradient_surface(
                slot_surface, ORANGE_NEON, CHARTREUSE, self.cell_width, self.cell_height
            )

        self.decoration_images = [
            pygame.image.load(f"{SLOT_MACHINE_IMAGE_PATH}deco{i}.png").convert_alpha()
            for i in range(1, 5)
        ]
        self.decoration_size = (100, 100)
        self.decoration_images = [
            pygame.transform.scale(img, self.decoration_size)
            for img in self.decoration_images
        ]

        self.winner_sound = pygame.mixer.Sound(f"{SLOT_MACHINE_AUDIO_PATH}win.mp3")
        self.lose_sound = pygame.mixer.Sound(f"{SLOT_MACHINE_AUDIO_PATH}lose.mp3")

        self.show_winner_message: bool = False
        self.winner_message_font_size: int = 150
        self.winner_message_rect_padding: int = 20
        self.winner_message_border_thickeness: int = 19
        self.winner_message_border_radius: int = 20

        self.additional_display_time = 4000

        self.show_loss_message: bool = False
        self.loss_message_font_size: int = 70
        self.loss_message_rect_padding: int = 20
        self.loss_message_border_thickeness: int = 5
        self.loss_message_border_radius: int = 20

        self.font_path: str = f"{SLOT_MACHINE_FONT_PATH}HackNerdFont-BoldItalic.ttf"

        self.init_joystick()

    def init_joystick(self) -> None:
        """Initialize the joystick if available."""
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            print(f"Joystick connected: {self.joystick.get_name()}")
        else:
            print("No joystick detected.")

    def get_state(self) -> str:
        """
        Get the current state of the button.

        Returns:
            str: The current state of the button.
        """
        button_state = self.shared_data.get_value_state("active_button")
        return button_state

    def is_winner_attemp(self) -> bool:
        """
        Check if the current attempt is a winning attempt.

        Returns:
            bool: True if the attempt is a winning attempt, False otherwise.
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
        """Draw a gradient background on the given surface."""
        for i in range(height):
            color = (
                color_top[0] + (color_bottom[0] - color_top[0]) * i / height,
                color_top[1] + (color_bottom[1] - color_top[1]) * i / height,
                color_top[2] + (color_bottom[2] - color_top[2]) * i / height,
            )
            pygame.draw.line(surface, color, (0, i), (width, i))

    def draw_grid(self) -> None:
        """Draw the grid for the slot machine."""
        total_width = 3 * self.cell_width
        total_height = self.cell_height
        grid_x = (self.WIDTH - total_width) // 2
        grid_y = (self.HEIGHT - total_height) // 2

        for col in range(3):
            x = grid_x + col * self.cell_width
            y = grid_y
            cell_bg_rect = (x, y, self.cell_width, self.cell_height)

            clip_rect = pygame.Rect(x, y, self.cell_width, self.cell_height)
            self.screen.set_clip(clip_rect)
            self.screen.blit(self.slot_gradients[col], (x, y))
            self.screen.set_clip(None)

            pygame.draw.rect(
                self.screen,
                COOL_GRAY_LIGHT,
                cell_bg_rect,
                LINE_WIDHT,
                border_radius=self.border_radius,
            )

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
        for i in range(3):
            x = (self.WIDTH - 3 * self.cell_width) // 2 + i * self.cell_width
            y = (self.HEIGHT - self.cell_height) // 2

            reduced_size = (250, 250)
            slot_image = pygame.transform.scale(
                self.slot_winner_images[self.slots[i]], reduced_size
            )

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
        if state_message:
            font = pygame.font.Font(self.font_path, font_size)
            winner_text = font.render(message, True, font_color)
            text_rect = winner_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))

            rect_width = text_rect.width + 2 * padding
            rect_height = text_rect.height + 2 * padding
            rect_x = text_rect.centerx - rect_width // 2
            rect_y = text_rect.centery - rect_height // 2
            rect = pygame.Rect(rect_x, rect_y, rect_width, rect_height)

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
        for slot_surface in self.slot_gradients:
            self.draw_gradient_surface(
                slot_surface, color_top, color_bottom, self.cell_width, self.cell_height
            )

    def spin_slots(self) -> None:

        self.slot_images = self.slot_regular_images

        spin_time = [random.randint(3000, 5000) for _ in range(3)]
        start_time = [
            pygame.time.get_ticks() + random.randint(0, 500) for _ in range(3)
        ]
        end_time = [st + spin for st, spin in zip(start_time, spin_time)]
        finished_slots = [False] * 3
        running = True

        self.change_colors(ORANGE_NEON, CHARTREUSE)
        self.draw_gradient_surface(
            self.gradient_surface, AQUAMARINE, ORANGE_NEON, self.WIDTH, self.HEIGHT
        )
        self.shared_data.set_value_game_state("state", "PROCESANDO...")

        while running:
            current_time = pygame.time.get_ticks()
            running = False
            for i in range(3):
                if current_time < end_time[i]:
                    running = True
                    self.slots[i] = (self.slots[i] + 1) % len(self.slot_images)
                else:
                    finished_slots[i] = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.blit(self.gradient_surface, (0, 0))
            self.draw_grid()
            self.draw_slots()
            pygame.display.flip()
            self.clock.tick(FPS // 5)

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
            pygame.time.delay(1000)
            self.draw_gradient_surface(
                self.gradient_surface, ORANGE_NEON, ORANGE_NEON, self.WIDTH, self.HEIGHT
            )
            self.lose_sound.play()
            self.show_loss_message = True
            self.show_winner_message = False
            pygame.time.set_timer(pygame.USEREVENT, self.additional_display_time + 3500)
            self.shared_data.set_value_game_state("state", "PERDEDOR")

        self.display_final_result()

    def spin_to_winner(self) -> None:
        winner_frame = 7
        steps_needed = [
            (winner_frame - slot) % len(self.slot_winner_images) for slot in self.slots
        ]

        running = True
        while running:
            running = False
            for i in range(3):
                if steps_needed[i] > 0:
                    running = True
                    self.slots[i] = (self.slots[i] + 1) % len(self.slot_winner_images)
                    steps_needed[i] -= 1

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.blit(self.gradient_surface, (0, 0))
            self.draw_grid()
            self.draw_slots()
            pygame.display.flip()
            self.clock.tick(FPS // 5)

        self.slot_images = self.slot_regular_images

    def stop_slots(self, finished_slots: list[bool]) -> None:

        winners = [
            random.randint(0, len(self.slot_regular_images) - 1) for _ in range(3)
        ]
        for i in range(3):
            if not finished_slots[i]:
                self.slots[i] = winners[i]

    def display_final_result(self) -> None:
        for i in reversed(range(3)):
            slot_end_time = pygame.time.get_ticks() + (3 - i) * 500
            while pygame.time.get_ticks() < slot_end_time:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                self.screen.blit(self.gradient_surface, (0, 0))
                self.draw_grid()
                self.draw_slots()
                pygame.display.flip()
                self.clock.tick(FPS)

    def stop(self) -> None:
        """Stop the slot machine game and clean up resources."""
        self.winner_sound.stop()
        self.lose_sound.stop()
        self.running = False
        self.show_winner_message = False
        self.show_loss_message = False
        # Reset game state
        self.slots = [0, 0, 0]
        self.spin_count = self.internal_data.get_counter()

    def display_final_message(self) -> None:
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

    def run(self, screen) -> None:
        """Run the slot machine game loop."""
        self.running = True
        self.start_time = pygame.time.get_ticks()
        counter = self.internal_data.get_counter()

        if not hasattr(self, 'screen'):
            self.screen = screen

        state_button = self.get_state()
        if state_button == "True":
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN and event.button == 0:
                    self.spin_count = counter = self.internal_data.get_counter()
                    counter += 1
                    self.internal_data.set_env_variable("COUNTER", f"{counter}")
                    self.spin_slots()
                    self.shared_data.set_value_state("active_button", "False")

                if event.type == pygame.USEREVENT:
                    self.show_winner_message = False
                    self.show_loss_message = False

        self.draw_gradient_surface(
            self.gradient_surface, AQUAMARINE, ORANGE_NEON, self.WIDTH, self.HEIGHT
        )
        self.delta_time = (pygame.time.get_ticks() - self.start_time) / 1000
        screen.blit(self.gradient_surface, (0, 0))
        self.draw_grid()
        self.draw_slots()
        self.display_final_message()

if __name__ == "__main__":
    slot_machine = SlotMachine()
    slot_machine.run()
