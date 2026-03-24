"""
Flappy Bird Clone
A Python/Pygame implementation of the classic Flappy Bird game.
"""

import pygame
import random
import sys

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Screen dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# Frame rate
FPS = 60

# Physics
GRAVITY = 0.5          # Pixels per frame² pulled downward
FLAP_STRENGTH = -9     # Upward velocity applied on each flap

# Bird
BIRD_X = 80            # Horizontal position (fixed)
BIRD_RADIUS = 18       # Collision radius used for drawing and hit-testing
BIRD_MAX_FALL = 12     # Terminal (downward) velocity

# Pipes
PIPE_WIDTH = 60
PIPE_GAP = 150         # Vertical space the bird must fly through
PIPE_SPEED = 3         # Pixels per frame (scroll speed)
PIPE_SPAWN_INTERVAL = 90  # Frames between new pipe pairs
PIPE_MIN_HEIGHT = 60   # Minimum visible height of a pipe section
PIPE_MAX_HEIGHT = SCREEN_HEIGHT - PIPE_GAP - PIPE_MIN_HEIGHT  # Maximum top-pipe height

# Ground
GROUND_HEIGHT = 80     # Height of the ground strip at the bottom
GROUND_Y = SCREEN_HEIGHT - GROUND_HEIGHT

# Colors
COLOR_SKY = (113, 197, 207)       # Sky blue
COLOR_GROUND = (222, 184, 135)    # Sandy ground
COLOR_GROUND_TOP = (100, 200, 80) # Bright grass strip on ground top edge
COLOR_PIPE = (75, 175, 75)        # Green pipe body
COLOR_PIPE_DARK = (50, 140, 50)   # Darker green for pipe cap shading
COLOR_PIPE_CAP = (60, 160, 60)    # Pipe cap color
COLOR_BIRD_BODY = (255, 210, 50)  # Yellow/orange bird body
COLOR_BIRD_WING = (255, 165, 0)   # Wing accent
COLOR_BIRD_EYE = (255, 255, 255)  # Eye white
COLOR_BIRD_PUPIL = (30, 30, 30)   # Eye pupil
COLOR_BIRD_BEAK = (255, 100, 50)  # Beak
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_SCORE = (255, 255, 255)
COLOR_OVERLAY = (0, 0, 0, 150)    # Semi-transparent overlay (used via Surface)
COLOR_TITLE = (255, 220, 50)      # Title text
COLOR_GAMEOVER = (220, 60, 60)    # Game-over text
COLOR_SUBTITLE = (220, 220, 220)  # Instruction text
COLOR_PANEL = (50, 80, 120)       # Score-panel background
COLOR_PANEL_BORDER = (200, 220, 255)

# Game states
STATE_START = "start"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"


# ---------------------------------------------------------------------------
# Helper drawing functions
# ---------------------------------------------------------------------------

def draw_pipe(surface: pygame.Surface, x: int, top_height: int) -> None:
    """Draw a pipe pair (top + bottom) at horizontal position *x*.

    Parameters
    ----------
    surface:
        Pygame surface to draw onto.
    x:
        Left edge of the pipe pair in screen coordinates.
    top_height:
        Pixel height of the top pipe (measured from y=0 downward).
    """
    bottom_y = top_height + PIPE_GAP  # Top edge of the bottom pipe
    bottom_height = GROUND_Y - bottom_y

    cap_width = PIPE_WIDTH + 12   # Caps are slightly wider than the shaft
    cap_height = 18
    cap_x = x - 6                  # Centre the cap over the shaft

    # --- Top pipe ---
    pygame.draw.rect(surface, COLOR_PIPE, (x, 0, PIPE_WIDTH, top_height))
    # Cap
    pygame.draw.rect(surface, COLOR_PIPE_CAP, (cap_x, top_height - cap_height, cap_width, cap_height))
    # Highlight stripe on left edge
    pygame.draw.rect(surface, COLOR_PIPE_DARK, (x, 0, 6, top_height))

    # --- Bottom pipe ---
    pygame.draw.rect(surface, COLOR_PIPE, (x, bottom_y, PIPE_WIDTH, bottom_height))
    # Cap
    pygame.draw.rect(surface, COLOR_PIPE_CAP, (cap_x, bottom_y, cap_width, cap_height))
    # Highlight stripe
    pygame.draw.rect(surface, COLOR_PIPE_DARK, (x, bottom_y, 6, bottom_height))


def draw_bird(surface: pygame.Surface, cx: int, cy: int, tilt: float) -> None:
    """Draw the bird character centred at (*cx*, *cy*) with a visual *tilt*.

    Parameters
    ----------
    surface:
        Pygame surface to draw onto.
    cx, cy:
        Center coordinates of the bird.
    tilt:
        Current vertical velocity; used to rotate the bird visually.
    """
    # Clamp tilt angle for display
    angle = max(-30, min(tilt * -3, 70))

    # Body
    pygame.draw.circle(surface, COLOR_BIRD_BODY, (cx, cy), BIRD_RADIUS)

    # Wing (a small ellipse offset slightly downward and to the left)
    wing_surf = pygame.Surface((BIRD_RADIUS, BIRD_RADIUS // 2), pygame.SRCALPHA)
    pygame.draw.ellipse(wing_surf, COLOR_BIRD_WING, wing_surf.get_rect())
    rotated_wing = pygame.transform.rotate(wing_surf, -angle)
    surface.blit(rotated_wing, (cx - BIRD_RADIUS // 2 - 4, cy + 2))

    # Eye white
    eye_x = cx + 8
    eye_y = cy - 6
    pygame.draw.circle(surface, COLOR_BIRD_EYE, (eye_x, eye_y), 6)
    # Pupil
    pygame.draw.circle(surface, COLOR_BIRD_PUPIL, (eye_x + 1, eye_y + 1), 3)

    # Beak
    beak_points = [
        (cx + BIRD_RADIUS - 2, cy),
        (cx + BIRD_RADIUS + 8, cy - 3),
        (cx + BIRD_RADIUS + 8, cy + 3),
    ]
    pygame.draw.polygon(surface, COLOR_BIRD_BEAK, beak_points)


def draw_ground(surface: pygame.Surface, offset: int) -> None:
    """Draw a scrolling ground strip.

    Parameters
    ----------
    surface:
        Pygame surface to draw onto.
    offset:
        Horizontal scroll offset (pixels) used to animate the ground texture.
    """
    # Main sandy fill
    pygame.draw.rect(surface, COLOR_GROUND, (0, GROUND_Y, SCREEN_WIDTH, GROUND_HEIGHT))
    # Grass strip
    pygame.draw.rect(surface, COLOR_GROUND_TOP, (0, GROUND_Y, SCREEN_WIDTH, 8))

    # Simple stripe pattern to give the impression of movement
    stripe_spacing = 40
    for i in range(-1, SCREEN_WIDTH // stripe_spacing + 2):
        sx = (i * stripe_spacing - offset % stripe_spacing)
        pygame.draw.line(surface, COLOR_GROUND, (sx, GROUND_Y + 12), (sx + 20, GROUND_Y + 12), 2)


def draw_background(surface: pygame.Surface) -> None:
    """Draw the static sky background with a few decorative clouds."""
    surface.fill(COLOR_SKY)

    # Simple cloud blobs
    cloud_positions = [(60, 80), (180, 50), (300, 100), (370, 60)]
    for cx, cy in cloud_positions:
        pygame.draw.ellipse(surface, COLOR_WHITE, (cx - 30, cy - 15, 60, 30))
        pygame.draw.ellipse(surface, COLOR_WHITE, (cx - 20, cy - 25, 40, 30))
        pygame.draw.ellipse(surface, COLOR_WHITE, (cx + 5, cy - 20, 35, 28))


def draw_text_centered(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    color: tuple,
    y: int,
) -> None:
    """Render *text* horizontally centred at vertical position *y*."""
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(centerx=SCREEN_WIDTH // 2, top=y)
    surface.blit(rendered, rect)


# ---------------------------------------------------------------------------
# Game classes
# ---------------------------------------------------------------------------

class Bird:
    """Represents the player-controlled bird."""

    def __init__(self) -> None:
        self.x = BIRD_X
        self.y = SCREEN_HEIGHT // 2 - 50
        self.velocity = 0.0   # Positive = moving downward

    # ------------------------------------------------------------------
    def flap(self) -> None:
        """Apply an upward impulse (flap)."""
        self.velocity = FLAP_STRENGTH

    # ------------------------------------------------------------------
    def update(self) -> None:
        """Apply gravity and move the bird one frame."""
        self.velocity += GRAVITY
        self.velocity = min(self.velocity, BIRD_MAX_FALL)
        self.y += self.velocity

    # ------------------------------------------------------------------
    def get_rect(self) -> pygame.Rect:
        """Return a tight bounding rectangle used for collision detection."""
        r = BIRD_RADIUS - 4   # Slightly smaller than visual radius = more forgiving
        return pygame.Rect(self.x - r, self.y - r, r * 2, r * 2)

    # ------------------------------------------------------------------
    def is_out_of_bounds(self) -> bool:
        """Return True if the bird has hit the ceiling or the ground."""
        return self.y - BIRD_RADIUS < 0 or self.y + BIRD_RADIUS >= GROUND_Y

    # ------------------------------------------------------------------
    def draw(self, surface: pygame.Surface) -> None:
        draw_bird(surface, int(self.x), int(self.y), self.velocity)


class Pipe:
    """A single pipe pair (top + bottom) that scrolls left."""

    def __init__(self, x: int) -> None:
        self.x = x
        # Random top-pipe height
        self.top_height = random.randint(PIPE_MIN_HEIGHT, PIPE_MAX_HEIGHT)
        self.scored = False    # True once the bird has passed this pipe

    # ------------------------------------------------------------------
    @property
    def bottom_y(self) -> int:
        """Top edge of the bottom pipe."""
        return self.top_height + PIPE_GAP

    # ------------------------------------------------------------------
    def update(self) -> None:
        """Move the pipe to the left by one frame."""
        self.x -= PIPE_SPEED

    # ------------------------------------------------------------------
    def is_off_screen(self) -> bool:
        """Return True once the pipe has scrolled past the left edge."""
        return self.x + PIPE_WIDTH + 12 < 0   # +12 for cap overhang

    # ------------------------------------------------------------------
    def collides_with(self, bird: Bird) -> bool:
        """Return True if the bird's bounding rect overlaps this pipe pair."""
        bird_rect = bird.get_rect()

        # Top-pipe rectangle
        top_rect = pygame.Rect(self.x - 6, 0, PIPE_WIDTH + 12, self.top_height)
        # Bottom-pipe rectangle
        bottom_rect = pygame.Rect(
            self.x - 6,
            self.bottom_y,
            PIPE_WIDTH + 12,
            GROUND_Y - self.bottom_y,
        )
        return bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect)

    # ------------------------------------------------------------------
    def draw(self, surface: pygame.Surface) -> None:
        draw_pipe(surface, self.x, self.top_height)


class Game:
    """Main game controller that manages state, entities, and rendering."""

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy Bird")
        self.clock = pygame.time.Clock()

        # Fonts
        self.font_large = pygame.font.SysFont("Arial", 52, bold=True)
        self.font_medium = pygame.font.SysFont("Arial", 32, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 22)

        # Initialize game entities / counters
        self._reset()

    # ------------------------------------------------------------------
    def _reset(self) -> None:
        """Reset all game entities to their initial state (new game)."""
        self.bird = Bird()
        self.pipes: list[Pipe] = []
        self.score = 0
        self.high_score = getattr(self, "high_score", 0)  # Preserve across resets
        self.frame_count = 0
        self.ground_offset = 0
        self.state = STATE_START

    # ------------------------------------------------------------------
    def _spawn_pipe(self) -> None:
        """Add a new pipe pair just off the right edge of the screen."""
        self.pipes.append(Pipe(SCREEN_WIDTH + 20))

    # ------------------------------------------------------------------
    def _handle_flap_event(self) -> None:
        """Trigger a flap and handle state transitions."""
        if self.state == STATE_START:
            self.state = STATE_PLAYING
            self.bird.flap()
        elif self.state == STATE_PLAYING:
            self.bird.flap()
        elif self.state == STATE_GAME_OVER:
            self._reset()
            self.state = STATE_PLAYING
            self.bird.flap()

    # ------------------------------------------------------------------
    def _process_events(self) -> None:
        """Process all pending pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP):
                    self._handle_flap_event()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self._handle_flap_event()

    # ------------------------------------------------------------------
    def _update(self) -> None:
        """Update all game entities for one frame (only during gameplay)."""
        if self.state != STATE_PLAYING:
            return

        self.frame_count += 1
        self.ground_offset = (self.ground_offset + PIPE_SPEED) % 40

        # Bird physics
        self.bird.update()

        # Spawn pipes at regular intervals
        if self.frame_count % PIPE_SPAWN_INTERVAL == 0:
            self._spawn_pipe()

        # Update pipes and check scoring / collisions
        for pipe in self.pipes:
            pipe.update()

            # Score: bird centre passes the right edge of the pipe
            if not pipe.scored and pipe.x + PIPE_WIDTH < self.bird.x:
                pipe.scored = True
                self.score += 1
                self.high_score = max(self.high_score, self.score)

            # Collision
            if pipe.collides_with(self.bird):
                self.state = STATE_GAME_OVER
                return

        # Remove off-screen pipes
        self.pipes = [p for p in self.pipes if not p.is_off_screen()]

        # Ground / ceiling collision
        if self.bird.is_out_of_bounds():
            self.state = STATE_GAME_OVER

    # ------------------------------------------------------------------
    def _draw_start_screen(self) -> None:
        """Draw the start/title screen."""
        draw_background(self.screen)
        draw_ground(self.screen, 0)

        # Draw a static bird for aesthetics
        draw_bird(self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60, 0)

        # Title
        draw_text_centered(self.screen, "FLAPPY BIRD", self.font_large, COLOR_TITLE, 120)

        # Instruction panel
        panel_rect = pygame.Rect(60, 280, 280, 110)
        panel_surf = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        panel_surf.fill((*COLOR_PANEL, 200))
        self.screen.blit(panel_surf, panel_rect.topleft)
        pygame.draw.rect(self.screen, COLOR_PANEL_BORDER, panel_rect, 2, border_radius=8)

        draw_text_centered(self.screen, "Press SPACE or Click", self.font_small, COLOR_WHITE, 295)
        draw_text_centered(self.screen, "to start the game", self.font_small, COLOR_WHITE, 325)
        draw_text_centered(self.screen, "Avoid the pipes!", self.font_small, COLOR_SUBTITLE, 358)

        if self.high_score > 0:
            draw_text_centered(
                self.screen,
                f"Best: {self.high_score}",
                self.font_medium,
                COLOR_TITLE,
                430,
            )

    # ------------------------------------------------------------------
    def _draw_playing_screen(self) -> None:
        """Draw the active gameplay screen."""
        draw_background(self.screen)

        for pipe in self.pipes:
            pipe.draw(self.screen)

        draw_ground(self.screen, self.ground_offset)
        self.bird.draw(self.screen)

        # Score (top-center) with a drop shadow for readability
        shadow = self.font_large.render(str(self.score), True, COLOR_BLACK)
        shadow_rect = shadow.get_rect(centerx=SCREEN_WIDTH // 2 + 2, top=42)
        self.screen.blit(shadow, shadow_rect)
        draw_text_centered(self.screen, str(self.score), self.font_large, COLOR_SCORE, 40)

    # ------------------------------------------------------------------
    def _draw_game_over_screen(self) -> None:
        """Draw the game-over overlay on top of the last playing frame."""
        draw_background(self.screen)

        for pipe in self.pipes:
            pipe.draw(self.screen)

        draw_ground(self.screen, self.ground_offset)
        self.bird.draw(self.screen)

        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))

        # "Game Over" text
        draw_text_centered(self.screen, "GAME OVER", self.font_large, COLOR_GAMEOVER, 130)

        # Score panel
        panel_rect = pygame.Rect(80, 220, 240, 140)
        panel_surf = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        panel_surf.fill((*COLOR_PANEL, 220))
        self.screen.blit(panel_surf, panel_rect.topleft)
        pygame.draw.rect(self.screen, COLOR_PANEL_BORDER, panel_rect, 2, border_radius=8)

        draw_text_centered(self.screen, f"Score: {self.score}", self.font_medium, COLOR_WHITE, 235)
        draw_text_centered(self.screen, f"Best:  {self.high_score}", self.font_medium, COLOR_TITLE, 278)

        # Restart instruction
        draw_text_centered(self.screen, "Press SPACE or Click", self.font_small, COLOR_SUBTITLE, 380)
        draw_text_centered(self.screen, "to play again", self.font_small, COLOR_SUBTITLE, 408)

    # ------------------------------------------------------------------
    def _draw(self) -> None:
        """Select and execute the appropriate draw routine for the current state."""
        if self.state == STATE_START:
            self._draw_start_screen()
        elif self.state == STATE_PLAYING:
            self._draw_playing_screen()
        elif self.state == STATE_GAME_OVER:
            self._draw_game_over_screen()

        pygame.display.flip()

    # ------------------------------------------------------------------
    def run(self) -> None:
        """Main game loop."""
        while True:
            self._process_events()
            self._update()
            self._draw()
            self.clock.tick(FPS)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    game = Game()
    game.run()
