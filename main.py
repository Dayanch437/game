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
        
        # Game variables
        self.total_coins = len(self.coins)
        
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
        # Update player
        self.player.update(self.platforms)
        
        # Update enemies
        for enemy in self.enemies:
            enemy.update()
        
        # Update coins (for animation)
        for coin in self.coins:
            coin.update()
            
        # Check coin collection
        for coin in self.coins:
            if not coin.collected and self.player.rect.colliderect(coin.rect):
                coin.collected = True
                self.player.score += 10
                
        # Check enemy collision (only if not invincible)
        if not self.player.invincible:
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
                    
        # Check if player falls off screen
        if self.player.rect.top > SCREEN_HEIGHT:
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
            "HOW TO PLAY:",
            "",
            "🏃 Move: Arrow Keys or A/D",
            "⬆️  Jump: SPACE, UP, or W",
            "💰 Collect all coins to WIN!",
            "👾 Avoid the green enemies",
            "❤️  You have 5 lives",
            "",
            "TIPS:",
            "• You get 2 seconds invincibility after being hit",
            "• Jump higher and move faster!",
            "• Explore all platforms for coins",
            "",
            "Press ENTER to Start",
            "Press ESC to Quit"
        ]
        
        y = 180
        for instruction in instructions:
            if instruction.startswith("HOW") or instruction.startswith("TIPS"):
                text = self.small_font.render(instruction, True, BLUE)
            elif instruction == "":
                y += 10
                continue
            else:
                text = self.small_font.render(instruction, True, BLACK)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(text, text_rect)
            y += 30
            
    def draw_game(self):
        """Draw game elements"""
        # Draw platforms
        for platform in self.platforms:
            platform.draw(self.screen)
            
        # Draw coins
        for coin in self.coins:
            coin.draw(self.screen)
            
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)
            
        # Draw player
        self.player.draw(self.screen)
        
        # Draw HUD
        self.draw_hud()
        
    def draw_hud(self):
        """Draw heads-up display (score, lives)"""
        # HUD background panel
        hud_bg = pygame.Surface((200, 110))
        hud_bg.set_alpha(180)
        hud_bg.fill((50, 50, 50))
        self.screen.blit(hud_bg, (5, 5))
        
        # Score with icon
        score_text = self.small_font.render(f"⭐ Score: {self.player.score}", True, YELLOW)
        self.screen.blit(score_text, (15, 15))
        
        # Lives with heart icons
        lives_text = self.small_font.render(f"❤️  Lives:", True, RED)
        self.screen.blit(lives_text, (15, 45))
        # Draw heart icons for lives
        for i in range(self.player.lives):
            heart_x = 100 + i * 20
            if heart_x < 195:  # Don't overflow panel
                heart = self.small_font.render("❤️", True, RED)
                self.screen.blit(heart, (heart_x, 45))
        
        # Coins collected with progress bar
        coins_collected = sum(1 for coin in self.coins if coin.collected)
        coins_text = self.small_font.render(f"💰 Coins: {coins_collected}/{self.total_coins}", True, YELLOW)
        self.screen.blit(coins_text, (15, 75))
        
        # Progress bar for coins
        bar_width = 170
        bar_height = 10
        bar_x = 15
        bar_y = 95
        # Background bar
        pygame.draw.rect(self.screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
        # Progress bar
        progress = (coins_collected / self.total_coins) * bar_width
        pygame.draw.rect(self.screen, YELLOW, (bar_x, bar_y, progress, bar_height))
        # Border
        pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        
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
