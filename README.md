# SaveWaterGame

SaveWaterGame is a small Pygame awareness game about saving water. Move the tank, catch falling water drops, and build the highest score while protecting your remaining lives.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

The game loads visual and audio assets from its own directory, so it can be launched from any working directory.

## Controls

- **Left Arrow / Right Arrow:** Move the tank.
- **Enter or Space:** Start a round from the menu.
- **P:** Pause or resume the round.
- **M:** Toggle sound.
- **R:** Restart from the game-over screen.
- **Esc:** Return to the menu or quit from the menu.

## Gameplay

Catch water drops to increase the score. A missed drop costs one life. The falling speed and spawn rate increase gradually, but the difficulty remains bounded. When the round ends, the game displays the final score and stores the best score locally in `highscore.json`.

## Project files

- `main.py`: game states, rendering, input, scoring, audio, and persistence.
- `classes.py`: `Tank` and `Water` gameplay entities.
- `requirements.txt`: Python dependency list.
- `PRODUCT_SPEC.md`: client-focused redesign, UX definition, acceptance criteria, and feature roadmap.

## Product direction

The game is designed as a short, friendly awareness experience. The visual system uses a dark navy playfield, water-blue actions, clear score/lives feedback, and explicit start, pause, and game-over states. Future releases can add conservation tips, difficulty modes, accessibility options, and reviewed educational content.
