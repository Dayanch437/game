"""
Enemy class - moves back and forth on platforms
"""
import pygame
from constants import *


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, platform_left, platform_right):
        super().__init__()
        self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
        self.image.fill(ENEMY_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Movement boundaries (patrol area)
        self.platform_left = platform_left
        self.platform_right = platform_right
        self.vel_x = ENEMY_SPEED
        
    def update(self):
        # Move enemy
        self.rect.x += self.vel_x
        
        # Reverse direction at boundaries
        if self.rect.right >= self.platform_right or self.rect.left <= self.platform_left:
            self.vel_x = -self.vel_x
            
    def draw(self, screen):
        """Draw enemy with enhanced visuals"""
        # Main body with border
        pygame.draw.rect(screen, ENEMY_COLOR, self.rect)
        pygame.draw.rect(screen, (0, 150, 0), self.rect, 3)  # Darker border
        
        # Draw angry eyes
        eye_size = 5
        eye_white_size = 7
        # Left eye
        pygame.draw.circle(screen, WHITE, (self.rect.left + 12, self.rect.top + 12), eye_white_size)
        pygame.draw.circle(screen, BLACK, (self.rect.left + 12, self.rect.top + 12), eye_size)
        # Right eye  
        pygame.draw.circle(screen, WHITE, (self.rect.right - 12, self.rect.top + 12), eye_white_size)
        pygame.draw.circle(screen, BLACK, (self.rect.right - 12, self.rect.top + 12), eye_size)
        
        # Draw angry eyebrows
        pygame.draw.line(screen, BLACK, (self.rect.left + 6, self.rect.top + 6),
                        (self.rect.left + 18, self.rect.top + 8), 3)
        pygame.draw.line(screen, BLACK, (self.rect.right - 18, self.rect.top + 8),
                        (self.rect.right - 6, self.rect.top + 6), 3)
        
        # Draw zigzag mouth
        mouth_y = self.rect.bottom - 12
        points = [
            (self.rect.left + 8, mouth_y),
            (self.rect.centerx - 6, mouth_y + 5),
            (self.rect.centerx, mouth_y),
            (self.rect.centerx + 6, mouth_y + 5),
            (self.rect.right - 8, mouth_y)
        ]
        pygame.draw.lines(screen, BLACK, False, points, 3)


def create_enemies_level_1():
    """Create enemies for level 1"""
    enemies = []
    
    # Enemy on first platform (150, 450, width 150)
    enemies.append(Enemy(170, 410, 150, 300))
    
    # Enemy on second platform (400, 380, width 120)
    enemies.append(Enemy(420, 340, 400, 520))
    
    # Enemy on upper platform (300, 280, width 150)
    enemies.append(Enemy(320, 240, 300, 450))
    
    return enemies
