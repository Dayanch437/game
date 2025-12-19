"""
Simple 2D Endless Runner inspired by Subway Surfers (simplified).
- Three lanes, player runs automatically (obstacles move toward player)
- Left/Right to switch lanes instantly
- Jump to go over ground obstacles
- Slide to go under hanging obstacles
- Coins and distance-based scoring

Run: python3 endless_runner.py
Requires: pygame
"""

import sys
import random
import math
import pygame

# ------------- Settings -------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

LANE_COUNT = 3
LANE_X = [SCREEN_WIDTH * 0.25, SCREEN_WIDTH * 0.5, SCREEN_WIDTH * 0.75]
GROUND_Y = SCREEN_HEIGHT - 120  # y coordinate of the ground surface

PLAYER_WIDTH = 40
PLAYER_HEIGHT = 70
PLAYER_COLOR = (200, 40, 40)
PLAYER_SLIDE_HEIGHT = 36

OBSTACLE_WIDTH = 40
OBSTACLE_COLOR = (60, 60, 60)
HANGING_COLOR = (80, 40, 160)
COIN_COLOR = (255, 200, 40)

BASE_SCROLL_SPEED = 300.0  # pixels per second that world moves toward player
SPEED_INCREASE_RATE = 5.0  # pixels/sec per second (gradual accel)
SPAWN_INTERVAL = 0.9  # seconds between obstacle spawns (will randomize a bit)
COIN_SCORE = 5
DISTANCE_SCORE_RATE = 0.1  # points per pixel of scroll

FONT_COLOR = (20, 20, 20)
BG_COLOR = (135, 206, 235)

# ------------- Helper functions -------------

def clamp(v, lo, hi):
    return max(lo, min(hi, v))


# ------------- Sprite classes -------------
class Player(pygame.sprite.Sprite):
    """Player stays in one of three lanes. Switching lanes is instant.
    Jumping and sliding are implemented with simple vertical velocity and a slide timer.
    """

    def __init__(self):
        super().__init__()
        self.lane = 1  # start in middle lane (0..2)
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.color = PLAYER_COLOR

        # Position: x determined by lane, y by vertical motion
        self.x = LANE_X[self.lane]
        self.y = GROUND_Y - self.height
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.midbottom = (self.x, GROUND_Y)

        # Vertical movement
        self.vel_y = 0.0
        self.gravity = 1400.0  # pixels per second^2
        self.jump_speed = -650.0
        self.on_ground = True

        # Sliding
        self.sliding = False
        self.slide_time = 0.0
        self.max_slide_duration = 0.6

        # Stats
        self.score = 0

    def move_left(self):
        self.lane = clamp(self.lane - 1, 0, LANE_COUNT - 1)
        self.x = LANE_X[self.lane]
        self.rect.midbottom = (self.x, self.rect.bottom)

    def move_right(self):
        self.lane = clamp(self.lane + 1, 0, LANE_COUNT - 1)
        self.x = LANE_X[self.lane]
        self.rect.midbottom = (self.x, self.rect.bottom)

    def jump(self):
        if self.on_ground and not self.sliding:
            self.vel_y = self.jump_speed
            self.on_ground = False

    def start_slide(self):
        if self.on_ground and not self.sliding:
            self.sliding = True
            self.slide_time = 0.0
            # shrink collider
            old_mid = self.rect.midbottom
            self.rect.height = PLAYER_SLIDE_HEIGHT
            self.rect.width = self.width
            self.rect.midbottom = old_mid

    def stop_slide(self):
        if self.sliding:
            self.sliding = False
            old_mid = self.rect.midbottom
            self.rect.height = self.height
            self.rect.width = self.width
            self.rect.midbottom = old_mid

    def update(self, dt):
        # Slide timer
        if self.sliding:
            self.slide_time += dt
            if self.slide_time >= self.max_slide_duration:
                # Try to stop sliding; if there's space, stop
                self.stop_slide()

        # Apply gravity
        if not self.on_ground:
            self.vel_y += self.gravity * dt
            self.rect.y += int(self.vel_y * dt)

            # Check ground collision
            if self.rect.bottom >= GROUND_Y:
                self.rect.bottom = GROUND_Y
                self.on_ground = True
                self.vel_y = 0.0

        # Ensure x follows lane (instant lane switching)
        self.rect.centerx = int(self.x)

    def draw(self, surf):
        pygame.draw.rect(surf, self.color, self.rect)
        # simple eyes to hint direction/animation
        eye_radius = 3
        left_eye = (self.rect.centerx - 8, self.rect.centery - 10)
        right_eye = (self.rect.centerx + 8, self.rect.centery - 10)
        pygame.draw.circle(surf, (255, 255, 255), left_eye, eye_radius)
        pygame.draw.circle(surf, (255, 255, 255), right_eye, eye_radius)


class Obstacle(pygame.sprite.Sprite):
    """Obstacles appear in lanes and move left toward player.
    type='low' -> on ground, must jump over
    type='high' -> hanging, must slide under
    """

    def __init__(self, lane, x, kind='low'):
        super().__init__()
        self.lane = lane
        self.x = x
        self.kind = kind
        self.width = OBSTACLE_WIDTH

        if kind == 'low':
            self.height = 64
            self.color = OBSTACLE_COLOR
            # bottom aligned to ground
            self.rect = pygame.Rect(0, 0, self.width, self.height)
            self.rect.midbottom = (LANE_X[lane], GROUND_Y)
        else:  # 'high' hanging obstacle
            self.height = 32
            self.color = HANGING_COLOR
            self.rect = pygame.Rect(0, 0, self.width, self.height)
            # place hanging obstacle above ground so player must duck
            self.rect.midbottom = (LANE_X[lane], GROUND_Y - 60)

        self.rect.x = x

    def update(self, dt, scroll_speed):
        # Move toward left as world scrolls
        self.rect.x -= int(scroll_speed * dt)

    def draw(self, surf):
        pygame.draw.rect(surf, self.color, self.rect)
        # simple highlight
        pygame.draw.rect(surf, (0, 0, 0), self.rect, 2)


class Coin(pygame.sprite.Sprite):
    def __init__(self, lane, x, y_offset= -40):
        super().__init__()
        self.lane = lane
        self.x = x
        self.size = 18
        # position is relative to lane center
        cx = LANE_X[lane]
        cy = GROUND_Y - 10 + y_offset
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.rect.center = (cx, cy)
        self.collected = False
        self.pulse = 0.0

    def update(self, dt, scroll_speed):
        self.rect.x -= int(scroll_speed * dt)
        self.pulse += dt * 8.0

    def draw(self, surf):
        # simple pulsing circle
        r = int(self.size / 2 + math.sin(self.pulse) * 3)
        pygame.draw.circle(surf, COIN_COLOR, self.rect.center, r)
        pygame.draw.circle(surf, (0,0,0), self.rect.center, r, 2)


# ------------- Game class -------------
class EndlessRunnerGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('2D Endless Runner (Subway Surfers - style)')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 28)
        self.big_font = pygame.font.Font(None, 56)

        # Player
        self.player = Player()

        # Groups
        self.obstacles = []
        self.coins = []

        # Timers and speeds
        self.scroll_speed = BASE_SCROLL_SPEED
        self.spawn_timer = 0.0
        self.distance = 0.0

        # State
        self.state = 'menu'  # 'menu', 'playing', 'gameover'
        self.best_score = 0

    def reset(self):
        self.player = Player()
        self.obstacles = []
        self.coins = []
        self.scroll_speed = BASE_SCROLL_SPEED
        self.spawn_timer = 0.0
        self.distance = 0.0
        self.state = 'playing'

    def spawn_obstacle_or_coin(self):
        # Randomly spawn either an obstacle or a sequence of coins
        lane = random.randint(0, LANE_COUNT - 1)
        spawn_x = SCREEN_WIDTH + 60 + random.randint(0, 200)

        r = random.random()
        if r < 0.55:
            # obstacle
            kind = 'low' if random.random() < 0.6 else 'high'
            obs = Obstacle(lane, spawn_x, kind)
            self.obstacles.append(obs)
            # sometimes place a coin above a low obstacle
            if kind == 'low' and random.random() < 0.4:
                c = Coin(lane, spawn_x, y_offset=-60)
                self.coins.append(c)
        else:
            # coin line or arc - spawn 1-4 coins in this lane
            count = random.randint(1, 4)
            for i in range(count):
                cx = spawn_x + i * 50
                # half the time put in air
                y_off = -40 if random.random() < 0.6 else -10
                c = Coin(lane, cx, y_offset=y_off)
                self.coins.append(c)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if self.state == 'menu':
                    if event.key == pygame.K_RETURN:
                        self.reset()
                elif self.state == 'playing':
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        self.player.move_left()
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.player.move_right()
                    elif event.key in (pygame.K_UP, pygame.K_w, pygame.K_SPACE):
                        self.player.jump()
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.player.start_slide()
                elif self.state == 'gameover':
                    if event.key == pygame.K_RETURN or event.key == pygame.K_r:
                        self.reset()
            elif event.type == pygame.KEYUP:
                if self.state == 'playing':
                    if event.key in (pygame.K_DOWN, pygame.K_s):
                        self.player.stop_slide()

    def update(self, dt):
        if self.state != 'playing':
            return

        # increase speed gradually (simulating increased difficulty over time)
        self.scroll_speed += SPEED_INCREASE_RATE * dt

        # spawn logic
        self.spawn_timer += dt
        if self.spawn_timer >= SPAWN_INTERVAL:
            self.spawn_timer = 0.0
            # small random offset to spacing
            if random.random() < 0.9:
                self.spawn_obstacle_or_coin()

        # update player
        self.player.update(dt)

        # update obstacles and coins
        for obs in list(self.obstacles):
            obs.update(dt, self.scroll_speed)
            if obs.rect.right < -50:
                self.obstacles.remove(obs)

        for coin in list(self.coins):
            coin.update(dt, self.scroll_speed)
            if coin.rect.right < -50:
                self.coins.remove(coin)

        # collisions: coins
        for coin in list(self.coins):
            if self.player.rect.colliderect(coin.rect):
                self.player.score += COIN_SCORE
                try:
                    self.coins.remove(coin)
                except ValueError:
                    pass

        # collisions: obstacles
        for obs in self.obstacles:
            if self.player.rect.colliderect(obs.rect):
                # Determine if player is performing the correct evasive action
                if obs.kind == 'low':
                    # must be above obstacle (jumping) to avoid
                    if self.player.rect.bottom <= obs.rect.top + 5:
                        # safe
                        continue
                    else:
                        self.state = 'gameover'
                else:  # hanging
                    # must be sliding to pass under
                    if self.player.sliding:
                        continue
                    else:
                        self.state = 'gameover'

        # distance and score accrual
        self.distance += self.scroll_speed * dt
        self.player.score += int(self.scroll_speed * dt * DISTANCE_SCORE_RATE)

    def draw_ground_and_lanes(self, surf):
        # simple ground
        pygame.draw.rect(surf, (80, 50, 20), (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))
        # lane separators for visual guidance
        for i in range(LANE_COUNT):
            x = int(LANE_X[i])
            pygame.draw.line(surf, (220, 220, 220), (x, GROUND_Y - 220), (x, GROUND_Y), 2)

    def draw(self):
        self.screen.fill(BG_COLOR)

        if self.state == 'menu':
            title = self.big_font.render('ENDLESS RUNNER', True, (30, 30, 30))
            sub = self.font.render('Three lanes • Left/Right to change • Jump and Slide', True, FONT_COLOR)
            inst = self.font.render('Press ENTER to start', True, FONT_COLOR)
            self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 200)))
            self.screen.blit(sub, sub.get_rect(center=(SCREEN_WIDTH//2, 260)))
            self.screen.blit(inst, inst.get_rect(center=(SCREEN_WIDTH//2, 320)))
            # quick control hint
            hint = self.font.render('Arrows / WASD • Jump: up/space • Slide: down', True, FONT_COLOR)
            self.screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH//2, 360)))
            if self.best_score > 0:
                best = self.font.render(f'Best: {self.best_score}', True, FONT_COLOR)
                self.screen.blit(best, best.get_rect(center=(SCREEN_WIDTH//2, 400)))
            pygame.display.flip()
            return

        # playing or gameover: draw world
        self.draw_ground_and_lanes(self.screen)

        # draw coins
        for coin in self.coins:
            coin.draw(self.screen)

        # draw obstacles
        for obs in self.obstacles:
            obs.draw(self.screen)

        # draw player
        self.player.draw(self.screen)

        # HUD
        score_surf = self.font.render(f'Score: {self.player.score}', True, FONT_COLOR)
        dist_surf = self.font.render(f'Distance: {int(self.distance)}', True, FONT_COLOR)
        speed_surf = self.font.render(f'Speed: {int(self.scroll_speed)}', True, FONT_COLOR)
        self.screen.blit(score_surf, (12, 12))
        self.screen.blit(dist_surf, (12, 36))
        self.screen.blit(speed_surf, (12, 60))

        if self.state == 'gameover':
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0,0,0))
            self.screen.blit(overlay, (0,0))
            go = self.big_font.render('GAME OVER', True, (255, 80, 80))
            score = self.font.render(f'Score: {self.player.score}', True, (255,255,255))
            retry = self.font.render('Press ENTER or R to retry', True, (255,255,255))
            self.screen.blit(go, go.get_rect(center=(SCREEN_WIDTH//2, 220)))
            self.screen.blit(score, score.get_rect(center=(SCREEN_WIDTH//2, 300)))
            self.screen.blit(retry, retry.get_rect(center=(SCREEN_WIDTH//2, 360)))

        pygame.display.flip()

    def run(self):
        # Main loop
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_input()
            self.update(dt)
            self.draw()

            # When switching to gameover, capture best score
            if self.state == 'gameover':
                self.best_score = max(self.best_score, self.player.score)


# ------------- Explanations (in-code for learners) -------------
# Why lanes? -> Subway Surfers uses three lanes to give the player discrete left/right choices.
#   Implementation: lanes are fixed x positions (LANE_X). The player 'teleports' between lanes to keep controls simple.
# Why scrolling? -> The player feels like they're running forward when the world moves toward them.
#   Implementation: obstacles and coins move left by scroll_speed each frame; player stays horizontally fixed.
# Why jump/slide? -> To give two clear evasive options, matching Subway Surfers: jump over ground obstacles and slide under barriers.
#   Implementation: jump changes vertical velocity; slide temporarily reduces player's collider height.
# Why speed increases? -> To add difficulty and urgency over time like the original game.
#   Implementation: scroll_speed increases gradually by SPEED_INCREASE_RATE.


if __name__ == '__main__':
    try:
        game = EndlessRunnerGame()
        game.run()
    except ModuleNotFoundError as e:
        print('Missing dependency:', e)
        print('Install pygame: pip3 install pygame')
    except Exception as e:
        print('Error while running:', e)
        raise
