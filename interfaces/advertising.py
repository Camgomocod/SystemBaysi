import pygame
import moviepy.editor as mp
import os

from assets.config import(
    ADVERTISING_IMAGE_PATH,
    ADVERTISING_VIDEO_PATH,
    ADVERTISING_AUDIO_PATH,
    AQUAMARINE,
    ORANGE_NEON,
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
        pygame.display.set_caption("Advertising Interface")
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
        self.audio_started = False  # Nuevo flag para controlar el inicio del audio
        self.should_exit = False  # Nuevo flag para controlar la salida del bucle de video

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
        self.current_clip = None
        self.frame_iterator = None
        self.current_audio_path = None
        self.audio_index = 0
        self.is_stopping = False
        self.last_frame = None  # Guardar el último frame para evitar pantalla negra

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
        """Draw decorations on the screen."""
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
        try:
            if self.current_clip:
                self.cleanup_current_video()
            
            clip = mp.VideoFileClip(video_path)
            target_resolution = (576, 720)
            clip = clip.resize(newsize=target_resolution)
            return clip
        except Exception as e:
            print(f"Error loading video: {e}")
            return None

    def clip_to_surface(self, frame) -> pygame.Surface:
        """Convert a video frame to a Pygame surface.

        Args:
            frame (ndarray): The video frame as a NumPy array.

        Returns:
            Surface: The Pygame surface created from the video frame.
        """
        return pygame.image.frombuffer(frame.tobytes(), frame.shape[1::-1], "RGB")

    def get_temp_audio_path(self) -> str:
        """Genera una ruta única para cada archivo de audio temporal."""
        self.audio_index += 1
        return f"{ADVERTISING_AUDIO_PATH}temp_audio_{self.audio_index}.mp3"

    def load_audio_for_clip(self) -> bool:
        """Cargar y preparar el audio para el clip actual."""
        try:
            # Detener y limpiar audio anterior
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
            
            # Limpiar archivo anterior si existe
            if self.current_audio_path and os.path.exists(self.current_audio_path):
                try:
                    pygame.mixer.music.unload()
                    pygame.time.wait(100)  # Pequeña pausa para asegurar que se libere
                    os.remove(self.current_audio_path)
                except Exception as e:
                    print(f"Error removing old audio: {e}")

            # Generar nueva ruta para el audio
            self.current_audio_path = self.get_temp_audio_path()

            if self.current_clip and self.current_clip.audio:
                self.current_clip.audio.write_audiofile(self.current_audio_path, fps=44100)
                pygame.mixer.music.load(self.current_audio_path)
                pygame.mixer.music.play()
                self.audio_loaded = True
                return True
            return False

        except Exception as e:
            print(f"Error loading audio: {e}")
            self.audio_loaded = False
            return False

    def run(self, screen) -> None:
        """Render a single frame of the advertising video."""
        if not self.running or not self.video_files:
            return

        try:
            # Load the current video if not loaded
            if not hasattr(self, "current_clip") or self.current_clip is None:
                video_path = self.video_files[self.video_index]
                self.current_clip = self.load_and_resize_video(video_path)
                if self.current_clip is None:
                    return
                self.frame_iterator = self.current_clip.iter_frames(fps=8.3, dtype="uint8")
                self.start_audio(self.current_clip)

            # Mantener el último frame mientras se carga el siguiente video
            if self.last_frame is not None:
                screen.blit(self.gradient_surface, (0, 0))
                screen.blit(self.last_frame, ((self.screen_width - self.current_clip.size[0]) // 2, 0))
                self.draw_decorations(screen)

            try:
                frame = next(self.frame_iterator)
                surface = self.clip_to_surface(frame)
                self.last_frame = surface  # Guardar el frame actual
                
                screen.blit(self.gradient_surface, (0, 0))
                screen.blit(surface, ((self.screen_width - self.current_clip.size[0]) // 2, 0))
                self.draw_decorations(screen)
                
                # Sincronizar FPS con el video original
                self.clock.tick(10)
                
            except StopIteration:
                # Mantener el último frame mientras se prepara el siguiente video
                if self.last_frame is not None:
                    screen.blit(self.gradient_surface, (0, 0))
                    screen.blit(self.last_frame, ((self.screen_width - self.current_clip.size[0]) // 2, 0))
                    self.draw_decorations(screen)
                
                self.cleanup_current_video()
                self.video_index = (self.video_index + 1) % len(self.video_files)
                self.current_clip = None
                self.frame_iterator = None
                return

        except Exception as e:
            print(f"Error en reproducción: {e}")
            self.cleanup_current_video()

    def start_audio(self, clip: mp.VideoFileClip) -> None:
        """Start the audio playback of the video."""
        self.current_audio_path = f"{ADVERTISING_AUDIO_PATH}temp_audio_{self.audio_index}.mp3"
        try:
            if os.path.exists(self.current_audio_path):
                os.remove(self.current_audio_path)
            
            clip.audio.write_audiofile(self.current_audio_path, fps=44100)
            pygame.mixer.music.load(self.current_audio_path)
            pygame.mixer.music.play()
            self.audio_index += 1
        except Exception as e:
            print(f"Error processing audio: {e}")

    def cleanup_current_video(self):
        """Limpiar recursos del video actual."""
        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
            
            if self.current_clip:
                self.current_clip.close()
                self.current_clip = None
            
            if self.current_audio_path and os.path.exists(self.current_audio_path):
                try:
                    os.remove(self.current_audio_path)
                except:
                    pass
                
        except Exception as e:
            print(f"Error limpiando recursos: {e}")

    def stop(self) -> None:
        """Stop video playback and clean up resources."""
        self.is_stopping = True
        self.running = False
        self.cleanup_current_video()
        
        # Limpiar todos los archivos de audio temporales
        for i in range(self.audio_index + 1):
            temp_path = f"{ADVERTISING_AUDIO_PATH}temp_audio_{i}.mp3"
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
        
        self.video_index = 0
        self.audio_index = 0
        pygame.time.wait(100)


