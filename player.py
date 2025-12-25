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
        self.immortal = True  # IMMORTAL MODE - player never dies!
        
        # Double jump feature
        self.can_double_jump = True
        self.has_double_jumped = False
        
        # Dash ability
        self.dash_speed = 20
        self.dash_duration = 10
        self.dash_cooldown = 40  # frames
        self.dash_timer = 0
        self.dash_cooldown_timer = 0
        self.is_dashing = False
        
        # Combo system
        self.combo = 0
        self.combo_timer = 0
        self.combo_max_time = 180  # 3 seconds to continue combo
        
        # Power-up modifiers
        self.speed_boost = 1.0
        self.jump_boost = 1.0
        
    def update(self, platforms, speed_boost=1.0, jump_boost=1.0):
        # Store power-up modifiers
        self.speed_boost = speed_boost
        self.jump_boost = jump_boost
        # Update invincibility timer
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
        
        # Update combo timer
        if self.combo_timer > 0:
            self.combo_timer -= 1
            if self.combo_timer <= 0:
                self.combo = 0
        
        # Update dash cooldown
        if self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer -= 1
        
        # Update dash
        if self.is_dashing:
            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.is_dashing = False
        
        # Get key presses
        keys = pygame.key.get_pressed()
        
        # Dash ability (Shift key)
        if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and not self.is_dashing and self.dash_cooldown_timer == 0:
            self.is_dashing = True
            self.dash_timer = self.dash_duration
            self.dash_cooldown_timer = self.dash_cooldown
        
        # Horizontal movement with acceleration
        target_vel_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            target_vel_x = -PLAYER_SPEED * self.speed_boost
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            target_vel_x = PLAYER_SPEED * self.speed_boost
            self.facing_right = True
        
        # Apply dash speed boost
        if self.is_dashing:
            if self.facing_right:
                target_vel_x = self.dash_speed * self.speed_boost
            else:
                target_vel_x = -self.dash_speed * self.speed_boost
        
        # Smooth acceleration
        if target_vel_x != 0:
            self.vel_x = target_vel_x
        else:
            self.vel_x *= 0.8  # Smooth deceleration
            
        # Jumping with double jump
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]):
            if self.on_ground:
                self.vel_y = JUMP_STRENGTH * self.jump_boost
                self.on_ground = False
                self.has_double_jumped = False
            elif self.can_double_jump and not self.has_double_jumped:
                # Double jump!
                self.vel_y = JUMP_STRENGTH * 0.85 * self.jump_boost  # Slightly weaker than first jump
                self.has_double_jumped = True
            
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
        
        # Draw dash trail effect
        if self.is_dashing:
            for i in range(3):
                trail_alpha = 50 - (i * 15)
                trail_surf = pygame.Surface((self.rect.width, self.rect.height))
                trail_surf.set_alpha(trail_alpha)
                trail_surf.fill(BLUE)
                offset = i * 8
                if self.facing_right:
                    screen.blit(trail_surf, (self.rect.x - offset, self.rect.y))
                else:
                    screen.blit(trail_surf, (self.rect.x + offset, self.rect.y))
        
        # Draw immortal glow effect
        if self.immortal:
            glow_size = 5
            glow_surf = pygame.Surface((self.rect.width + glow_size*2, self.rect.height + glow_size*2))
            glow_surf.set_alpha(100)
            glow_surf.fill(YELLOW)
            screen.blit(glow_surf, (self.rect.x - glow_size, self.rect.y - glow_size))
            
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
    
    def add_combo(self):
        """Add to combo counter"""
        self.combo += 1
        self.combo_timer = self.combo_max_time
        
    def get_combo_multiplier(self):
        """Get score multiplier based on combo"""
        if self.combo < 3:
            return 1
        elif self.combo < 5:
            return 1.5
        elif self.combo < 10:
            return 2
        else:
            return 3
