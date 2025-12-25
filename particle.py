"""
Particle effects system for visual excitement
"""
import pygame
import random
import math
from constants import *


class Particle:
    def __init__(self, x, y, color, vel_x=0, vel_y=0, lifetime=30, size=4):
        self.x = x
        self.y = y
        self.color = color
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.gravity = 0.3
        
    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += self.gravity
        self.lifetime -= 1
        
    def is_dead(self):
        return self.lifetime <= 0
        
    def draw(self, screen):
        alpha = int((self.lifetime / self.max_lifetime) * 255)
        surf = pygame.Surface((self.size * 2, self.size * 2))
        surf.set_alpha(alpha)
        surf.set_colorkey((0, 0, 0))
        pygame.draw.circle(surf, self.color, (self.size, self.size), self.size)
        screen.blit(surf, (int(self.x - self.size), int(self.y - self.size)))


class ParticleSystem:
    def __init__(self):
        self.particles = []
        
    def emit_jump(self, x, y):
        """Emit particles when player jumps"""
        for _ in range(8):
            angle = random.uniform(0.5 * math.pi, 1.5 * math.pi)  # Downward spread
            speed = random.uniform(2, 5)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            color = random.choice([WHITE, (200, 200, 255), (150, 150, 200)])
            self.particles.append(Particle(x, y, color, vel_x, vel_y, lifetime=25))
            
    def emit_landing(self, x, y):
        """Emit particles when player lands"""
        for _ in range(10):
            angle = random.uniform(-0.3 * math.pi, -0.7 * math.pi)  # Upward spread
            speed = random.uniform(1, 4)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            color = random.choice([(200, 200, 200), (150, 150, 150), WHITE])
            self.particles.append(Particle(x, y, color, vel_x, vel_y, lifetime=20))
            
    def emit_dash(self, x, y, facing_right):
        """Emit particles when player dashes"""
        for _ in range(3):
            vel_x = random.uniform(-2, 2)
            vel_y = random.uniform(-1, 1)
            if facing_right:
                vel_x -= 3
            else:
                vel_x += 3
            color = random.choice([BLUE, (100, 150, 255), (50, 100, 200)])
            self.particles.append(Particle(x, y, color, vel_x, vel_y, lifetime=15, size=5))
            
    def emit_coin_collect(self, x, y):
        """Emit particles when collecting a coin"""
        for _ in range(12):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            color = random.choice([YELLOW, (255, 215, 0), (255, 255, 100)])
            self.particles.append(Particle(x, y, color, vel_x, vel_y, lifetime=30, size=3))
            
    def emit_combo(self, x, y):
        """Emit particles for combo effects"""
        for _ in range(5):
            angle = random.uniform(-math.pi/2, -math.pi/6)
            speed = random.uniform(1, 3)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            color = random.choice([(255, 100, 255), (255, 50, 200), (200, 100, 255)])
            self.particles.append(Particle(x, y, color, vel_x, vel_y, lifetime=35, size=4))
            
    def update(self):
        # Update all particles
        for particle in self.particles:
            particle.update()
        # Remove dead particles
        self.particles = [p for p in self.particles if not p.is_dead()]
        
    def draw(self, screen):
        for particle in self.particles:
            particle.draw(screen)
            
    def clear(self):
        self.particles = []
