# SaveWaterGame

SaveWaterGame is a polished Pygame awareness game about saving water. Move the tank through an animated storm, catch falling drops, build combos, and collect special power-ups.

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

Catch water drops to increase the score. Consecutive catches build a combo and increase the score multiplier up to `x5`. Missing a drop costs one life and resets the combo. The storm becomes more intense as levels increase, with faster drops, denser rain, and a shorter spawn interval.

During a round, special icons can appear:

- **Shield:** Protects the tank from one missed drop.
- **Lightning bonus:** Adds five points immediately.

Catch and power-up events include animated particles and banner feedback. The game stores the best score locally in `highscore.json`.

## Visual features

The interface uses a storm-themed navy and aqua palette, animated rain streaks, custom vector-style HUD icons, a level progress bar, shield status, combo text, power-up icons, tank shadow, and catch/miss particles. No extra icon package is required; the icons are drawn procedurally by Pygame.

## Project files

- `main.py`: game states, rendering, rain animation, input, scoring, combos, power-ups, particles, audio, and persistence.
- `classes.py`: `Tank`, `Water`, `RainDrop`, `Particle`, and `PowerUp` gameplay entities.
- `requirements.txt`: Python dependency list.
- `PRODUCT_SPEC.md`: client-focused redesign, UX definition, acceptance criteria, and feature roadmap.

## Product direction

The game is designed as a short, friendly awareness experience that feels like a small arcade product rather than a prototype. Future releases can add conservation tips, difficulty modes, accessibility options, localization, and reviewed educational content.
