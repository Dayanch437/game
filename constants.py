"""
Game Constants and Settings
"""

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
SKY_BLUE = (135, 206, 235)

# Physics
GRAVITY = 0.6  # Even gentler gravity for more air control
JUMP_STRENGTH = -18  # Much higher jump for excitement!
PLAYER_SPEED = 8  # Faster movement for better control
ENEMY_SPEED = 1.5  # Slower enemies

# Player settings
PLAYER_WIDTH = 45
PLAYER_HEIGHT = 45
PLAYER_COLOR = RED
INVINCIBILITY_TIME = 120  # 2 seconds at 60 FPS

# Platform settings
PLATFORM_HEIGHT = 20
GROUND_HEIGHT = 50

# Enemy settings
ENEMY_WIDTH = 40
ENEMY_HEIGHT = 40
ENEMY_COLOR = GREEN

# Coin settings
COIN_SIZE = 20
COIN_COLOR = YELLOW

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2
WIN = 3
