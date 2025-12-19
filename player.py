"""
Player character class
"""
import pygame
from constants import *


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill(PLAYER_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Movement
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True
        
        # Stats
        self.score = 0
        self.lives = 5  # More lives!
        self.invincible = False
        self.invincible_timer = 0
        
    def update(self, platforms):
        # Update invincibility timer
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
        
        # Get key presses
        keys = pygame.key.get_pressed()
        
        # Horizontal movement with acceleration
        target_vel_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            target_vel_x = -PLAYER_SPEED
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            target_vel_x = PLAYER_SPEED
            self.facing_right = True
        
        # Smooth acceleration
        if target_vel_x != 0:
            self.vel_x = target_vel_x
        else:
            self.vel_x *= 0.8  # Smooth deceleration
            
        # Jumping
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False
            
        # Apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 20:  # Terminal velocity
            self.vel_y = 20
            
        # Update position
        self.rect.x += self.vel_x
        self.check_collisions_x(platforms)
        
        self.rect.y += self.vel_y
        self.on_ground = False
        self.check_collisions_y(platforms)
        
        # Keep player on screen (horizontally)
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            
    def check_collisions_x(self, platforms):
        """Check horizontal collisions with platforms"""
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_x > 0:  # Moving right
                    self.rect.right = platform.rect.left
                elif self.vel_x < 0:  # Moving left
                    self.rect.left = platform.rect.right
                    
    def check_collisions_y(self, platforms):
        """Check vertical collisions with platforms"""
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:  # Falling down
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:  # Jumping up
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0
                    
    def draw(self, screen):
        """Draw player with enhanced visual"""
        # Flash when invincible
        if self.invincible and self.invincible_timer % 10 < 5:
            return  # Skip drawing to create flash effect
            
        # Main body with gradient effect (simulate by drawing multiple rects)
        pygame.draw.rect(screen, PLAYER_COLOR, self.rect)
        pygame.draw.rect(screen, (255, 50, 50), self.rect, 3)  # Border
        
        # Draw eyes
        eye_size = 6
        eye_y = self.rect.top + 15
        if self.facing_right:
            eye_x = self.rect.right - 18
        else:
            eye_x = self.rect.left + 18
        
        # White of eye
        pygame.draw.circle(screen, WHITE, (eye_x, eye_y), eye_size)
        # Pupil
        pygame.draw.circle(screen, BLACK, (eye_x, eye_y), eye_size - 2)
        
        # Draw smile
        mouth_y = self.rect.top + 30
        if self.facing_right:
            mouth_start = (self.rect.right - 25, mouth_y)
            mouth_end = (self.rect.right - 10, mouth_y)
        else:
            mouth_start = (self.rect.left + 10, mouth_y)
            mouth_end = (self.rect.left + 25, mouth_y)
        pygame.draw.line(screen, BLACK, mouth_start, mouth_end, 3)
