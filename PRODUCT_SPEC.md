# SaveWaterGame: Client Product Specification

## Product direction

SaveWaterGame should feel like a short, polished awareness game rather than a technical prototype. The player should understand the objective within five seconds, start with one obvious action, receive immediate feedback after every catch or miss, and always know what to do next.

The redesigned experience uses a water-blue visual identity, a dark high-contrast playfield, a clear score area, visible lives, and short gameplay sessions. The tone is positive and action-oriented: the game should make water conservation memorable without interrupting the fun.

## Primary user journey

The user opens the game and sees a focused start screen with the title, the message “Every drop counts,” the best score, and a single play action. During play, the user moves the tank with the left and right arrow keys. Water drops fall at a controlled pace. A successful catch increases the score and plays a short sound. A missed drop removes one life. When the round ends, the user sees the score, best score, and a clear option to restart.

The player can pause with `P`, toggle audio with `M`, and return to the menu with `Esc`. These controls are visible on the start screen so the user does not have to guess.

## UI/UX redesign

### Visual system

The interface uses deep navy as the base surface, light blue for water and primary actions, green for positive feedback, orange for progression, and red only for lives and missed drops. Text is grouped into a clear hierarchy: a large title, a readable action label, and muted supporting instructions. Panels use rounded corners and a thin blue outline to create a compact arcade-style presentation.

### Screen definitions

| Screen | Purpose | Required elements |
|---|---|---|
| Start screen | Explain the game and start a round | Title, short value statement, play action, controls, best score |
| Gameplay screen | Keep the user focused on catching drops | Score, lives, game title, falling drops, tank |
| Pause screen | Let the user safely stop | “Paused” label, resume instruction, menu instruction |
| Game-over screen | Close the round and motivate replay | Final score, best score, replay instruction, menu instruction |

### Feedback behavior

A catch should produce three forms of feedback: the drop disappears, the score changes, and a short sound plays. A miss should reduce the visible life count and play a different short sound. The game should not flash the whole screen or use unreadable text because the playfield is small and action is fast.

## Implemented MVP features

The first redesign release includes a menu state, gameplay state, pause state, and game-over state. It also includes a persistent best score stored locally, a mute toggle, safe loading of assets relative to the source file, delta-time movement, a bounded spawn difficulty curve, clamped tank movement, and safe removal of caught or missed drops.

## Prioritized feature roadmap

### Release 1: polished core game

The current implementation should ship with the redesigned screens, reliable collision handling, a stable difficulty curve, a restart flow, and a high-score indicator. This release establishes a complete round lifecycle and removes the most visible prototype defects.

### Release 2: engagement and awareness

Add a short conservation tip after every round. Examples include “Turn off the tap while brushing” and “Fix leaking taps early.” Add a combo indicator for consecutive catches and a small celebration when the player reaches a score milestone. Keep these elements optional and brief so they do not interrupt play.

### Release 3: progression

Introduce three difficulty modes: Relaxed, Standard, and Challenge. Relaxed mode should use slower drops and more lives. Challenge mode should increase speed and reduce the spawn interval. Store the best score separately for each mode.

### Release 4: content and accessibility

Add keyboard remapping, a reduced-motion option, a no-audio option in settings, color-safe life indicators, and localized text. A simple tutorial overlay can demonstrate the tank movement before the first round.

### Release 5: community and education

Add a weekly conservation challenge, a shareable score card, and a small fact screen containing verified water-saving guidance. Any public leaderboard should be considered only after privacy, moderation, and account requirements are defined.

## Acceptance criteria for the redesigned MVP

The user can start a round without reading a separate document. The tank cannot leave the screen. A catch always increases the score by exactly one. A missed drop always reduces lives by exactly one. Multiple simultaneous catches or misses do not get skipped. The user can pause, resume, restart after game over, toggle audio, and return to the menu. The game can be launched from any working directory because assets are resolved relative to the source file. The best score remains available after restarting the application.

## Product risks and decisions

The game should avoid adding too many visual effects before the core loop is stable. A leaderboard should not be implemented as a local-only feature because users may assume scores are shared or verified. Educational tips should be short and reviewed before publication. The game should remain playable without audio and should not depend on a network connection.

## Suggested success measures

The first measurable goal is successful round completion: users should be able to open the game, start a round, and understand the controls without support. The next measures are replay rate, average score, average round duration, and the percentage of sessions in which a player reaches the game-over screen. If analytics are added later, they should be opt-in and privacy-conscious.
