"""
Super Mario-like Platformer Game
Main game loop and logic
"""
import pygame
import sys
from constants import *
from player import Player
from platform import Platform, create_level_1
from enemy import Enemy, create_enemies_level_1
from coin import Coin, create_coins_level_1
from particle import ParticleSystem
from powerup import PowerUp, PowerUpEffect, create_powerups_level_1


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Super Platformer Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Game state
        self.state = MENU
        self.reset_game()
        
    def reset_game(self):
        """Reset game to initial state"""
        # Create player
        self.player = Player(50, SCREEN_HEIGHT - GROUND_HEIGHT - PLAYER_HEIGHT - 10)
        
        # Create level
        self.platforms = create_level_1()
        self.enemies = create_enemies_level_1()
        self.coins = create_coins_level_1()
        self.powerups = create_powerups_level_1()
        
        # Particle system
        self.particles = ParticleSystem()
        
        # Power-up effects
        self.active_powerups = []
        
        # Game variables
        self.total_coins = len(self.coins)
        
        # Track player state for particle effects
        self.player_was_on_ground = False
        self.player_was_dashing = False
        
    def run(self):
        """Main game loop"""
        running = True
        while running:
            self.clock.tick(FPS)
            
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_RETURN:
                        if self.state == MENU:
                            self.state = PLAYING
                        elif self.state == GAME_OVER or self.state == WIN:
                            self.reset_game()
                            self.state = PLAYING
                            
            # Update
            if self.state == PLAYING:
                self.update()
            
            # Draw
            self.draw()
            pygame.display.flip()
            
        pygame.quit()
        sys.exit()
        
    def update(self):
        """Update game logic"""
        # Emit dash particles
        if self.player.is_dashing and not self.player_was_dashing:
            self.particles.emit_dash(self.player.rect.centerx, self.player.rect.centery, self.player.facing_right)
        self.player_was_dashing = self.player.is_dashing
        
        # Emit jump particles
        if not self.player.on_ground and self.player_was_on_ground:
            self.particles.emit_jump(self.player.rect.centerx, self.player.rect.bottom)
        
        # Emit landing particles
        if self.player.on_ground and not self.player_was_on_ground:
            self.particles.emit_landing(self.player.rect.centerx, self.player.rect.bottom)
        
        self.player_was_on_ground = self.player.on_ground
        
        # Update player with power-up effects
        speed_boost = 1.0
        jump_boost = 1.0
        
        for effect in self.active_powerups:
            if effect.type == PowerUp.SPEED_BOOST:
                speed_boost = 1.5
            elif effect.type == PowerUp.MEGA_JUMP:
                jump_boost = 1.4
        
        self.player.update(self.platforms, speed_boost, jump_boost)
        
        # Update enemies
        for enemy in self.enemies:
            enemy.update()
        
        # Update coins (for animation)
        for coin in self.coins:
            coin.update()
            
        # Update power-ups
        for powerup in self.powerups:
            powerup.update()
        
        # Update particles
        self.particles.update()
        
        # Update active power-up timers
        for effect in self.active_powerups:
            effect.update()
        self.active_powerups = [e for e in self.active_powerups if not e.is_expired()]
            
        # Check coin collection with combo system
        for coin in self.coins:
            if not coin.collected and self.player.rect.colliderect(coin.rect):
                coin.collected = True
                self.player.add_combo()
                multiplier = self.player.get_combo_multiplier()
                
                # Apply score multiplier power-up
                if self.has_powerup(PowerUp.SCORE_MULTIPLIER):
                    multiplier *= 2
                    
                points = int(10 * multiplier)
                self.player.score += points
                self.particles.emit_coin_collect(coin.rect.centerx, coin.rect.centery)
                if self.player.combo > 2:
                    self.particles.emit_combo(self.player.rect.centerx, self.player.rect.top)
        
        # Check power-up collection
        for powerup in self.powerups:
            if not powerup.collected and self.player.rect.colliderect(powerup.rect):
                powerup.collected = True
                self.active_powerups.append(PowerUpEffect(powerup.powerup_type))
                self.player.score += 25
                self.particles.emit_coin_collect(powerup.rect.centerx, powerup.rect.centery)
                
        # Check enemy collision
        if self.player.immortal:
            # In immortal mode, colliding with enemies gives points and combo!
            for enemy in self.enemies:
                if self.player.rect.colliderect(enemy.rect) and not self.player.invincible:
                    self.player.invincible = True
                    self.player.invincible_timer = 30  # Short invincibility to prevent multiple hits
                    self.player.add_combo()
                    self.player.score += int(15 * self.player.get_combo_multiplier())
                    self.particles.emit_combo(self.player.rect.centerx, self.player.rect.top)
                    break
        elif not self.player.invincible:
            # Only take damage if not immortal and not invincible
            for enemy in self.enemies:
                if self.player.rect.colliderect(enemy.rect):
                    self.player.lives -= 1
                    self.player.invincible = True
                    self.player.invincible_timer = INVINCIBILITY_TIME
                    if self.player.lives <= 0:
                        self.state = GAME_OVER
                    else:
                        # Reset player position
                        self.player.rect.x = 50
                        self.player.rect.y = SCREEN_HEIGHT - GROUND_HEIGHT - PLAYER_HEIGHT - 10
                        self.player.vel_x = 0
                        self.player.vel_y = 0
                    break  # Only hit once
                    
        # Check if player falls off screen (immortal mode: just reset position)
        if self.player.rect.top > SCREEN_HEIGHT:
            if self.player.immortal:
                # Just reset position in immortal mode
                self.player.rect.x = 50
                self.player.rect.y = SCREEN_HEIGHT - GROUND_HEIGHT - PLAYER_HEIGHT - 10
                self.player.vel_x = 0
                self.player.vel_y = 0
            else:
                self.player.lives -= 1
                self.player.invincible = True
                self.player.invincible_timer = INVINCIBILITY_TIME
                if self.player.lives <= 0:
                    self.state = GAME_OVER
                else:
                    self.player.rect.x = 50
                    self.player.rect.y = SCREEN_HEIGHT - GROUND_HEIGHT - PLAYER_HEIGHT - 10
                    self.player.vel_x = 0
                    self.player.vel_y = 0
                
        # Check win condition (collect all coins)
        if all(coin.collected for coin in self.coins):
            self.state = WIN
                
    def has_powerup(self, powerup_type):
        """Check if player has a specific power-up active"""
        return any(e.type == powerup_type for e in self.active_powerups)
            
    def draw(self):
        """Draw everything"""
        # Background gradient (sky to lighter blue)
        for y in range(SCREEN_HEIGHT):
            color_value = 135 + int((y / SCREEN_HEIGHT) * 50)  # Gradient from darker to lighter
            pygame.draw.line(self.screen, (color_value, 206, 235), (0, y), (SCREEN_WIDTH, y))
        
        if self.state == MENU:
            self.draw_menu()
        elif self.state == PLAYING:
            self.draw_game()
        elif self.state == GAME_OVER:
            self.draw_game_over()
        elif self.state == WIN:
            self.draw_win()
            
    def draw_menu(self):
        """Draw main menu"""
        # Animated title
        title = self.font.render("🎮 SUPER PLATFORMER 🎮", True, RED)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        
        # Shadow effect for title
        title_shadow = self.font.render("🎮 SUPER PLATFORMER 🎮", True, BLACK)
        shadow_rect = title_shadow.get_rect(center=(SCREEN_WIDTH // 2 + 3, 103))
        self.screen.blit(title_shadow, shadow_rect)
        self.screen.blit(title, title_rect)
        
        instructions = [
            "HOW TO PLAY - ENHANCED EDITION:",
            "",
            "🏃 Move: Arrow Keys or A/D",
            "⬆️  Jump: SPACE, UP, or W (Double Jump!)",
            "⚡ Dash: SHIFT (Super Speed!)",
            "💰 Collect coins for combos!",
            "⭐ Collect power-ups!",
            "👾 Touch enemies for BONUS points!",
            "",
            "✨ NEW FEATURES:",
            "• 🛡️  IMMORTAL MODE - Never die!",
            "• 🔥 Double jump in mid-air",
            "• ⚡ Dash ability with cooldown",
            "• 🎯 Combo system for bonus points",
            "• ⭐ Power-ups: Speed, Jump, Score x2",
            "• 💫 Particle effects!",
            "",
            "Press ENTER to Start",
            "Press ESC to Quit"
        ]
        
        y = 150
        for instruction in instructions:
            if instruction.startswith("HOW") or instruction.startswith("✨"):
                text = self.small_font.render(instruction, True, BLUE)
            elif instruction == "":
                y += 10
                continue
            else:
                text = self.small_font.render(instruction, True, BLACK)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(text, text_rect)
            y += 25
            
    def draw_game(self):
        """Draw game elements"""
        # Draw platforms
        for platform in self.platforms:
            platform.draw(self.screen)
            
        # Draw coins
        for coin in self.coins:
            coin.draw(self.screen)
        
        # Draw power-ups
        for powerup in self.powerups:
            powerup.draw(self.screen)
            
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)
            
        # Draw particles (behind player)
        self.particles.draw(self.screen)
            
        # Draw player
        self.player.draw(self.screen)
        
        # Draw HUD
        self.draw_hud()
        
    def draw_hud(self):
        """Draw heads-up display (score, lives, combo, dash, etc.)"""
        # Main HUD background panel (larger to fit new info)
        hud_bg = pygame.Surface((220, 190))
        hud_bg.set_alpha(180)
        hud_bg.fill((50, 50, 50))
        self.screen.blit(hud_bg, (5, 5))
        
        # Score with icon
        score_text = self.small_font.render(f"⭐ Score: {self.player.score}", True, YELLOW)
        self.screen.blit(score_text, (15, 15))
        
        # Immortal mode indicator
        if self.player.immortal:
            immortal_text = self.small_font.render("🛡️  IMMORTAL MODE!", True, (255, 215, 0))
            self.screen.blit(immortal_text, (15, 40))
        else:
            # Lives with heart icons (only show if not immortal)
            lives_text = self.small_font.render(f"❤️  Lives:", True, RED)
            self.screen.blit(lives_text, (15, 40))
            # Draw heart icons for lives
            for i in range(min(self.player.lives, 8)):  # Max 8 hearts displayed
                heart_x = 100 + i * 20
                if heart_x < 215:  # Don't overflow panel
                    heart = self.small_font.render("❤️", True, RED)
                    self.screen.blit(heart, (heart_x, 40))
        
        # Combo counter (if active)
        if self.player.combo > 0:
            combo_color = (255, 100, 255) if self.player.combo >= 5 else (255, 200, 100)
            combo_text = self.small_font.render(f"🔥 COMBO x{self.player.combo}! ", True, combo_color)
            self.screen.blit(combo_text, (15, 65))
            multiplier_text = self.small_font.render(f"   ({self.player.get_combo_multiplier()}x points)", True, combo_color)
            self.screen.blit(multiplier_text, (15, 65))
        
        # Dash cooldown indicator
        dash_y = 90 if self.player.combo > 0 else 65
        if self.player.dash_cooldown_timer > 0:
            cooldown_pct = (self.player.dash_cooldown_timer / self.player.dash_cooldown) * 100
            dash_text = self.small_font.render(f"⚡ Dash: {int(cooldown_pct)}%", True, (150, 150, 150))
        else:
            dash_text = self.small_font.render("⚡ Dash: READY!", True, (100, 255, 100))
        self.screen.blit(dash_text, (15, dash_y))
        
        # Coins collected with progress bar
        coins_y = dash_y + 25
        coins_collected = sum(1 for coin in self.coins if coin.collected)
        coins_text = self.small_font.render(f"💰 Coins: {coins_collected}/{self.total_coins}", True, YELLOW)
        self.screen.blit(coins_text, (15, coins_y))
        
        # Progress bar for coins
        bar_width = 190
        bar_height = 10
        bar_x = 15
        bar_y = coins_y + 20
        # Background bar
        pygame.draw.rect(self.screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
        # Progress bar
        progress = (coins_collected / self.total_coins) * bar_width
        pygame.draw.rect(self.screen, YELLOW, (bar_x, bar_y, progress, bar_height))
        # Border
        pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Active power-ups display
        powerup_y = bar_y + 15
        if self.active_powerups:
            for i, effect in enumerate(self.active_powerups):
                if effect.type == PowerUp.SPEED_BOOST:
                    text = self.small_font.render(f"⚡ Speed: {effect.get_time_remaining():.1f}s", True, BLUE)
                elif effect.type == PowerUp.MEGA_JUMP:
                    text = self.small_font.render(f"🚀 Jump: {effect.get_time_remaining():.1f}s", True, (255, 100, 255))
                else:  # SCORE_MULTIPLIER
                    text = self.small_font.render(f"⭐ 2x Score: {effect.get_time_remaining():.1f}s", True, (255, 215, 0))
                self.screen.blit(text, (15, powerup_y + i * 20))
        
    def draw_game_over(self):
        """Draw game over screen"""
        # Dim background
        self.draw_game()
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over_text = self.font.render("GAME OVER", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, game_over_rect)
        
        score_text = self.font.render(f"Final Score: {self.player.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        self.screen.blit(score_text, score_rect)
        
        restart_text = self.small_font.render("Press ENTER to Restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        self.screen.blit(restart_text, restart_rect)
        
    def draw_win(self):
        """Draw win screen"""
        # Dim background
        self.draw_game()
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Win text
        win_text = self.font.render("YOU WIN!", True, YELLOW)
        win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(win_text, win_rect)
        
        score_text = self.font.render(f"Final Score: {self.player.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        self.screen.blit(score_text, score_rect)
        
        restart_text = self.small_font.render("Press ENTER to Play Again", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        self.screen.blit(restart_text, restart_rect)


if __name__ == "__main__":
    game = Game()
    game.run()
