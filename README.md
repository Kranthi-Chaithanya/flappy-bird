# Flappy Bird

A fully functional Flappy Bird clone written in Python using Pygame.

## Requirements

- Python 3.8 or higher
- Pygame 2.0 or higher

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/Kranthi-Chaithanya/flappy-bird.git
   cd flappy-bird
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

## Running the Game

```bash
python flappy_bird.py
```

## How to Play

| Action | Control |
|--------|---------|
| Flap / Start | **Spacebar**, **↑ Arrow**, or **Left Mouse Click** |
| Restart after Game Over | **Spacebar**, **↑ Arrow**, or **Left Mouse Click** |

- Guide the bird through the gaps between the pipes.
- Every pipe pair you pass through scores **1 point**.
- The game ends when the bird hits a pipe, the ground, or the ceiling.
- Your best score is saved for the duration of the session.

## Features

- Sky-blue background with decorative clouds
- Scrolling ground with grass
- Green pipes with caps
- Animated yellow/orange bird with wing and beak
- Start screen, active gameplay, and game-over screen
- Live score display and high-score tracking
- Smooth 60 FPS gameplay with gravity and flap physics