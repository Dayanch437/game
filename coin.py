"""
Collectible coins
"""
import pygame
from constants import *


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((COIN_SIZE, COIN_SIZE))
        self.image.fill(COIN_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.collected = False
        self.animation_offset = 0  # For floating animation
        self.original_y = y
        
    def update(self):
        """Animate coin floating"""
        if not self.collected:
            self.animation_offset += 0.1
            self.rect.y = self.original_y + int(pygame.math.Vector2(0, 3).rotate(self.animation_offset * 10).y)
        
    def draw(self, screen):
        if not self.collected:
            # Outer golden circle with shine effect
            pygame.draw.circle(screen, COIN_COLOR, self.rect.center, COIN_SIZE // 2)
            pygame.draw.circle(screen, (255, 215, 0), self.rect.center, COIN_SIZE // 2, 2)  # Gold border
            
            # Inner darker circle for depth
            pygame.draw.circle(screen, (200, 180, 0), self.rect.center, COIN_SIZE // 2 - 4)
            
            # Shine spot
            shine_pos = (self.rect.centerx - 3, self.rect.centery - 3)
            pygame.draw.circle(screen, (255, 255, 200), shine_pos, 3)
            
            # Dollar sign
            font = pygame.font.Font(None, 20)
            text = font.render("$", True, (100, 80, 0))
            text_rect = text.get_rect(center=self.rect.center)
            screen.blit(text, text_rect)


def create_coins_level_1():
    """Create coins for level 1"""
    coins = []
    
    # Coins on platforms
    coins.append(Coin(200, 420))
    coins.append(Coin(250, 420))
    coins.append(Coin(450, 350))
    coins.append(Coin(650, 420))
    coins.append(Coin(350, 250))
    coins.append(Coin(580, 170))
    coins.append(Coin(140, 150))
    
    return coins
