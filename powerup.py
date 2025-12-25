"""
Power-ups system
"""
import pygame
import random
import math
from constants import *


class PowerUp(pygame.sprite.Sprite):
    SPEED_BOOST = 0
    MEGA_JUMP = 1
    SCORE_MULTIPLIER = 2
    
    def __init__(self, x, y, powerup_type):
        super().__init__()
        self.powerup_type = powerup_type
        self.size = 30
        self.rect = pygame.Rect(x, y, self.size, self.size)
        self.collected = False
        self.animation_offset = 0
        self.animation_speed = 0.1
        
        # Set color and effect based on type
        if powerup_type == self.SPEED_BOOST:
            self.color = BLUE
            self.symbol = "⚡"
            self.name = "Speed Boost"
        elif powerup_type == self.MEGA_JUMP:
            self.color = (255, 100, 255)
            self.symbol = "🚀"
            self.name = "Mega Jump"
        else:  # SCORE_MULTIPLIER
            self.color = (255, 215, 0)
            self.symbol = "⭐"
            self.name = "2x Score"
            
    def update(self):
        # Floating animation
        self.animation_offset += self.animation_speed
        
    def draw(self, screen):
        if self.collected:
            return
            
        # Draw floating effect
        float_y = self.rect.y + math.sin(self.animation_offset) * 5
        
        # Draw glow
        glow_size = self.size + 10
        glow_surf = pygame.Surface((glow_size, glow_size))
        glow_surf.set_alpha(100)
        glow_surf.fill(self.color)
        screen.blit(glow_surf, (self.rect.x - 5, float_y - 5))
        
        # Draw main powerup
        pygame.draw.circle(screen, self.color, (self.rect.centerx, int(float_y + self.size//2)), self.size//2)
        pygame.draw.circle(screen, WHITE, (self.rect.centerx, int(float_y + self.size//2)), self.size//2, 3)
        
        # Draw symbol
        font = pygame.font.Font(None, 24)
        text = font.render(self.symbol, True, WHITE)
        text_rect = text.get_rect(center=(self.rect.centerx, int(float_y + self.size//2)))
        screen.blit(text, text_rect)


def create_powerups_level_1():
    """Create power-ups for level 1"""
    import math  # Import here to avoid circular import
    
    powerups = []
    
    # Speed boost on middle platform
    powerups.append(PowerUp(250, 350, PowerUp.SPEED_BOOST))
    
    # Mega jump on upper left
    powerups.append(PowerUp(200, 200, PowerUp.MEGA_JUMP))
    
    # Score multiplier on right side
    powerups.append(PowerUp(650, 300, PowerUp.SCORE_MULTIPLIER))
    
    return powerups


class PowerUpEffect:
    """Tracks active power-up effects on the player"""
    def __init__(self, powerup_type, duration=300):  # 5 seconds default
        self.type = powerup_type
        self.duration = duration
        self.timer = duration
        
    def update(self):
        self.timer -= 1
        
    def is_expired(self):
        return self.timer <= 0
        
    def get_time_remaining(self):
        return self.timer / 60  # Convert frames to seconds
