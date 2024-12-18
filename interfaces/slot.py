import pygame

# Interfaz 1 - Bienvenida
class Interface1:
    def run(self, screen):
        font = pygame.font.SysFont('Arial', 36)
        text = font.render("Bienvenido a la interfaz 1!", True, (255, 255, 255))
        screen.fill((0, 0, 0))  # Fondo negro
        screen.blit(text, (150, 200))

