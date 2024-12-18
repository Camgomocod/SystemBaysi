import pygame
import moviepy.editor as mp
import os

from assets.config import(
    ADVERTISING_IMAGE_PATH,
    ADVERTISING_VIDEO_PATH,
    ADVERTISING_AUDIO_PATH,
    AQUAMARINE,
    ORANGE_NEON,
    BLACK,
)

class Advertising:
    """Class to handle video playback with audio in a Pygame window."""

    def __init__(self) -> None:
        """Initialize Pygame, set up the display, and load video files."""
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.screen_width, self.screen_height = self.screen.get_size()
        self.gradient_surface = pygame.Surface((self.screen_width, self.screen_height))
        self.icon = pygame.image.load(f"{ADVERTISING_IMAGE_PATH}icon_plant.png")
        pygame.mouse.set_visible(False)
        pygame.display.set_caption("Interfaz Publicitaria")
        pygame.display.set_icon(self.icon)

        self.padding = 100
        self.side_padding = self.padding * 2

        self.video_files = [
            os.path.join(ADVERTISING_VIDEO_PATH, f)
            for f in os.listdir(ADVERTISING_VIDEO_PATH)
            if f.endswith(".mp4")
        ]

        self.running = True
        self.clock = pygame.time.Clock()
        self.video_index = 0

        self.decoration_images = {
            "top_left": pygame.image.load(f"{ADVERTISING_IMAGE_PATH}left_lamp.png"),
            "bottom_left": pygame.image.load(
                f"{ADVERTISING_IMAGE_PATH}right_plant.png"
            ),
            "bottom_right": pygame.image.load(
                f"{ADVERTISING_IMAGE_PATH}right_plant.png"
            ),
            "top_right": pygame.image.load(f"{ADVERTISING_IMAGE_PATH}left_lamp.png"),
        }

        self.draw_gradient_surface()
        self.resize_decoration_images()

    def draw_gradient_surface(self) -> None:
        """Draw a gradient background for the display surface."""
        for i in range(self.screen_height):
            color = (
                AQUAMARINE[0]
                + (ORANGE_NEON[0] - AQUAMARINE[0]) * i / self.screen_height,
                AQUAMARINE[1]
                + (ORANGE_NEON[1] - AQUAMARINE[1]) * i / self.screen_height,
                AQUAMARINE[2]
                + (ORANGE_NEON[2] - AQUAMARINE[2]) * i / self.screen_height,
            )
            pygame.draw.line(
                self.gradient_surface, color, (0, i), (self.screen_width, i)
            )

    def resize_decoration_images(self) -> None:
        """Resize decoration images for proper display on the screen."""
        self.decoration_images["top_left"] = pygame.transform.scale(
            self.decoration_images["top_left"],
            (self.screen_width // 11, self.screen_height // 7),
        )
        self.decoration_images["bottom_left"] = pygame.transform.scale(
            self.decoration_images["bottom_left"],
            (self.screen_width // 6, self.screen_height // 4),
        )
        self.decoration_images["bottom_right"] = pygame.transform.scale(
            self.decoration_images["bottom_right"],
            (self.screen_width // 6, self.screen_height // 4),
        )
        self.decoration_images["top_right"] = pygame.transform.scale(
            self.decoration_images["top_right"],
            (self.screen_width // 11, self.screen_height // 7),
        )
    
    def draw_decorations(self, screen) -> None:
        """Dibuja las decoraciones en la pantalla."""
        screen.blit(self.decoration_images["top_left"], (0, 0))
        screen.blit(
            self.decoration_images["bottom_left"],
            (
                0,
                self.screen_height - self.decoration_images["bottom_left"].get_height(),
            ),
        )
        screen.blit(
            self.decoration_images["bottom_right"],
            (
                self.screen_width - self.decoration_images["bottom_right"].get_width(),
                self.screen_height - self.decoration_images["bottom_right"].get_height(),
            ),
        )
        screen.blit(
            self.decoration_images["top_right"],
            (
                self.screen_width - self.decoration_images["top_right"].get_width(),
                0,
            ),
        )


    def load_and_resize_video(self, video_path: str) -> mp.VideoFileClip:
        """Load a video file and resize it to a target resolution.

        Args:
            video_path (str): The path to the video file.

        Returns:
            VideoFileClip: The resized video clip.
        """
        clip = mp.VideoFileClip(video_path)
        target_resolution = (576, 720)
        clip = clip.resize(newsize=target_resolution)
        return clip

    def clip_to_surface(self, frame) -> pygame.Surface:
        """Convert a video frame to a Pygame surface.

        Args:
            frame (ndarray): The video frame as a NumPy array.

        Returns:
            Surface: The Pygame surface created from the video frame.
        """
        return pygame.image.frombuffer(frame.tobytes(), frame.shape[1::-1], "RGB")

    def play_video_with_audio(self, clip: mp.VideoFileClip) -> bool:
        """Play the video clip with its audio in the Pygame window.

        Args:
            clip (VideoFileClip): The video clip to be played.

        Returns:
            bool: True if the video played successfully, False if interrupted.
        """
        audio_path = f"{ADVERTISING_AUDIO_PATH}temp_audio.mp3"

        try:
            clip.audio.write_audiofile(audio_path, fps=44100)

            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Error al procesar {e}")

        # Reproduce el video
        for frame in clip.iter_frames(fps=clip.fps, dtype="uint8"):
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                ):
                    pygame.mixer.music.stop()
                    pygame.mixer.music.unload()
                    os.remove(audio_path)
                    return False

            surface = self.clip_to_surface(frame)
            x_position = (self.screen_width - clip.size[0]) // 2
            y_position = 0

            self.screen.blit(self.gradient_surface, (0, 0))
            self.screen.blit(surface, (x_position, y_position))

            line_thickness = 50
            pygame.draw.line(
                self.screen, BLACK, (0, 0), (self.screen_width, 0), line_thickness
            )

            self.screen.blit(self.decoration_images["top_left"], (0, 0))
            self.screen.blit(
                self.decoration_images["bottom_left"],
                (
                    0,
                    self.screen_height
                    - self.decoration_images["bottom_left"].get_height(),
                ),
            )
            self.screen.blit(
                self.decoration_images["bottom_right"],
                (
                    self.screen_width
                    - self.decoration_images["bottom_right"].get_width(),
                    self.screen_height
                    - self.decoration_images["bottom_right"].get_height(),
                ),
            )
            self.screen.blit(
                self.decoration_images["top_right"],
                (
                    self.screen_width - self.decoration_images["top_right"].get_width(),
                    0,
                ),
            )

            pygame.display.flip()
            self.clock.tick(clip.fps)

        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        os.remove(audio_path)

        return True

    def run(self, screen) -> None:
        """Renderiza un solo cuadro del video publicitario."""
        if not self.running or not self.video_files:
            return

        # Cargar el video actual si no está cargado
        if not hasattr(self, "current_clip") or self.current_clip is None:
            video_path = self.video_files[self.video_index]
            self.current_clip = self.load_and_resize_video(video_path)
            self.frame_iterator = self.current_clip.iter_frames(fps=self.current_clip.fps, dtype="uint8")
            self.start_audio(self.current_clip)

        try:
            frame = next(self.frame_iterator)
        except StopIteration:
            # Pasar al siguiente video
            self.video_index = (self.video_index + 1) % len(self.video_files)
            self.current_clip = None
            self.frame_iterator = None
            return

        # Convertir el cuadro a una superficie y mostrarlo
        surface = self.clip_to_surface(frame)
        x_position = (self.screen_width - self.current_clip.size[0]) // 2
        screen.fill((0, 0, 0))  # Limpiar la pantalla antes de dibujar el nuevo cuadro
        screen.blit(self.gradient_surface, (0, 0))
        screen.blit(surface, (x_position, 0))
        self.draw_decorations(screen)  # Llamada al nuevo método

        # Asegúrate de que el FPS de la pantalla esté sincronizado con el video
        self.clock.tick(self.current_clip.fps)

    def start_audio(self, clip: mp.VideoFileClip) -> None:
        """Inicia la reproducción de audio del video."""
        audio_path = f"{ADVERTISING_AUDIO_PATH}temp_audio.mp3"
        try:
            clip.audio.write_audiofile(audio_path, fps=44100)
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Error al procesar el audio: {e}")



    def stop(self) -> None:
        """Stop video playback and clean up resources."""
        self.running = False
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()


        # No cerrar pygame.display.quit() ni pygame.quit() aquí para evitar cerrar la ventana principal


