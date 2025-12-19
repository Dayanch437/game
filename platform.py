"""
Platform class for ground and floating platforms
"""
import pygame
from constants import *


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=BROWN):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
    def draw(self, screen):
        """Draw platform with enhanced 3D-like effect"""
        # Main platform
        pygame.draw.rect(screen, BROWN, self.rect)
        
        # Top highlight (lighter brown)
        highlight_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 5)
        pygame.draw.rect(screen, (180, 100, 30), highlight_rect)
        
        # Side shadow (darker brown)
        shadow_rect = pygame.Rect(self.rect.x, self.rect.bottom - 5, self.rect.width, 5)
        pygame.draw.rect(screen, (90, 40, 10), shadow_rect)
        
        # Border
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        # Add brick pattern for ground
        if self.rect.height > 30:  # Only for ground/thick platforms
            for x in range(self.rect.x, self.rect.right, 40):
                for y in range(self.rect.y + 10, self.rect.bottom - 5, 20):
                    pygame.draw.line(screen, (100, 50, 15), (x, y), (x + 20, y), 1)


def create_level_1():
    """Create the first level with platforms"""
    platforms = []
    
    # Ground
    ground = Platform(0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT)
    platforms.append(ground)
    
    # Floating platforms
    platforms.append(Platform(150, 450, 150, PLATFORM_HEIGHT))
    platforms.append(Platform(400, 380, 120, PLATFORM_HEIGHT))
    platforms.append(Platform(600, 450, 150, PLATFORM_HEIGHT))
    platforms.append(Platform(300, 280, 150, PLATFORM_HEIGHT))
    platforms.append(Platform(550, 200, 120, PLATFORM_HEIGHT))
    platforms.append(Platform(100, 180, 100, PLATFORM_HEIGHT))
    
    return platforms
