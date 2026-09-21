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

## Release-quality features

The current release adds three selectable storm modes from **S Settings**: Relaxed, Standard, and Challenge. Each mode changes lives and storm speed. Every round also includes a mission to catch 15 drops. Completing it grants a bonus and shows a mission-complete banner.

Toxic waste obstacles appear later in a round, especially in Challenge mode. Hitting one costs a life unless the shield power-up blocks it. The game-over screen includes a short water-saving tip so the awareness message continues after the arcade round.


## Milestones and celebration flow

At 25, 50, 75, and 100 points, the storm automatically pauses and shows an animated celebration. The player can press **Enter**, **Space**, or **P** to continue the mission, or **Esc** to return to the menu. The 100-point milestone displays a special **Legendary Victory** message. Pressing `P` during normal play opens the improved pause screen, where `P`, `Enter`, or `Space` resumes the run.

## Firebase and Google Auth decision

Firebase Google Auth is **not required for the current desktop game**. The game is intentionally offline, stores the best score locally, and does not need accounts. Adding authentication now would add browser OAuth, token handling, account recovery, privacy, and deployment complexity without improving the core gameplay.

Firebase becomes appropriate if the product adds cloud saves, cross-device profiles, verified online leaderboards, achievements tied to accounts, or remote analytics. At that point, Firebase Authentication and Firestore can be introduced behind an optional online mode. The desktop client must use a public client configuration only and must never contain Firebase Admin or service-account secrets.

## Level-based worlds and event weather

The playfield now changes its atmosphere as the level rises:

- **Levels 1–2 — Calm Drizzle:** soft rain and a calm blue mood.
- **Levels 3–4 — Rainy Afternoon:** stronger rain with gold drops beginning to appear.
- **Levels 5–6 — Thunderstorm:** purple storm tint, thunder event banners, lightning flashes, and rainbow drops.
- **Level 7+ — Monsoon Surge:** the heaviest rain, warm gold accent, and the fastest event rhythm.

Special drops are intentionally matched to their feedback: normal drops give `+1`, gold drops give `+3`, and rainbow drops give `+5`. The active world name and event message remain visible in the HUD, while lightning events create a short interactive flash without stopping the game.
