# SaveWaterGame: Client Product Specification

## Product direction

SaveWaterGame should feel like a short, polished awareness game rather than a technical prototype. The player should understand the objective within five seconds, start with one obvious action, receive immediate feedback after every catch or miss, and always know what to do next.

The current advanced direction is **Storm Catcher**: a water-blue arcade experience in which the player protects a tank during an animated rainstorm. The storm gets more challenging over time, while combos and power-ups reward accurate play.

## Primary user journey

The user opens the game and sees a focused start screen with the title, the message “Every drop counts,” a best score, and a single play action. During play, the user moves the tank with the left and right arrow keys. Water drops fall through animated rain. A successful catch increases the score and combo, while a missed drop removes one life and resets the combo. When the round ends, the user sees the final score, level, and best combo with a clear option to restart.

The player can pause with `P`, toggle audio with `M`, and return to the menu with `Esc`. These controls are visible on the start screen so the user does not have to guess.

## UI/UX redesign

### Visual system

The interface uses deep storm navy as the base surface, aqua for water and primary actions, green for positive feedback, orange for progression and bonuses, purple for shields, and red only for danger. Text is grouped into a clear hierarchy. Panels use rounded corners and a thin blue outline to create a compact arcade-style presentation.

The visual layer now includes animated rain streaks, custom vector-style drop, heart, shield, and bonus icons, a level progress bar, a tank shadow, and short-lived particle bursts. These elements are intentionally drawn procedurally so the game does not need a separate icon library or network dependency.

### Screen definitions

| Screen | Purpose | Required elements |
|---|---|---|
| Start screen | Explain the game and start a round | Title, storm identity, play action, controls, best score |
| Gameplay screen | Keep the user focused on catching drops | Score, level, progress bar, hearts, combo, rain, drops, tank, power-up status |
| Pause screen | Let the user safely stop | “Paused” label, resume instruction, menu instruction |
| Game-over screen | Close the round and motivate replay | Final score, level, best combo, best score, replay instruction |

### Feedback behavior

A catch produces an immediate score change, a combo update, a short sound, and aqua particle feedback. A miss removes a heart, resets the combo, plays a different sound, and creates a red impact effect. Every fifth consecutive catch shows a combo banner and applies a higher multiplier. Power-ups show a clear colored icon and a short banner when collected.

## Implemented advanced features

The current release includes menu, gameplay, pause, and game-over states; persistent best score; mute toggle; safe asset loading; delta-time movement; bounded difficulty; clamped tank movement; safe collision removal; animated decorative rain; custom HUD icons; level progression; combo tracking with a maximum `x5` multiplier; catch and miss particles; a shield power-up; a lightning-style five-point bonus power-up; and a level progress bar.

### Feature behavior

| Feature | Player value | Current behavior |
|---|---|---|
| Animated rain | Gives the game a strong storm identity | Rain streaks move continuously behind gameplay and intensify by level |
| Combo multiplier | Rewards accurate play | Every five catches increases the score multiplier up to `x5` |
| Shield power-up | Provides recovery after a mistake | One missed drop is absorbed and the shield is consumed |
| Bonus power-up | Creates surprise rewards | Collecting it adds five points immediately |
| Particles | Makes actions feel responsive | Catch, miss, shield, and bonus events create colored bursts |
| Level progression | Provides a visible sense of challenge | Level increases every ten score points and affects speed/rain/spawn rate |
| Vector icons | Improves recognition at small size | Hearts, shield, drop, and lightning icons are rendered in Pygame |

## Future feature roadmap

### Release 2: awareness and retention

Add a short conservation tip after every round. Examples include “Turn off the tap while brushing” and “Fix leaking taps early.” Add a rotating daily mission such as “Catch 20 drops” or “Reach a 10-catch combo.” Keep messages optional and brief so they do not interrupt play.

### Release 3: progression

Introduce Relaxed, Standard, and Challenge modes. Relaxed mode should use slower drops and more lives. Challenge mode should increase speed and reduce the spawn interval. Store the best score separately for each mode.

### Release 4: content and accessibility

Add keyboard remapping, a reduced-motion option, a no-audio option in settings, color-safe life indicators, screen-reader-friendly text where supported, and localized text. A short tutorial overlay can demonstrate tank movement and power-ups before the first round.

### Release 5: education and community

Add a reviewed fact screen containing water-saving guidance, a weekly conservation challenge, and a shareable score card. Any public leaderboard should be considered only after privacy, moderation, and account requirements are defined.

## Acceptance criteria for the advanced release

The user can start a round without reading a separate document. The tank cannot leave the screen. A catch always increases the score and never gets skipped when multiple drops are removed in the same frame. A miss reduces lives exactly once unless a shield is active. Combos reset on a miss and increase score through the visible multiplier. Power-ups can be collected, show their purpose through icons, and apply their effect once. Rain, particles, and all four game states render without external network access. The best score remains available after restarting the application.

## Product risks and decisions

The game should avoid adding so many effects that falling drops become difficult to see. Power-up frequency should remain low enough that accurate movement is still the main skill. A leaderboard should not be implemented as a local-only feature because users may assume scores are shared or verified. Educational tips should be short and reviewed before publication. The game should remain playable without audio and should not depend on a network connection.

## Suggested success measures

The first measurable goal is successful round completion: users should be able to open the game, start a round, and understand the controls without support. The next measures are replay rate, average score, best combo, power-up collection rate, average round duration, and the percentage of sessions in which a player reaches the game-over screen. If analytics are added later, they should be opt-in and privacy-conscious.

## Release-quality systems now implemented

The game now includes a settings screen with Relaxed, Standard, and Challenge modes. Mode selection changes lives and speed before a round begins. A mission tracker asks the player to catch 15 drops and awards a bonus on completion. Toxic plastic waste appears as a new hazard and can be blocked once by the shield power-up. The game-over screen presents a rotating water-saving tip, allowing the awareness message to continue after the play session.

The release acceptance test covers settings navigation, mode selection, mission progress, obstacle collisions, shield protection, all game-state renders, and safe startup in a headless environment.

## Milestone celebration and victory UX

At 25, 50, 75, and 100 points, gameplay automatically pauses so the player can appreciate the achievement instead of being forced to continue playing continuously. The celebration screen uses an animated trophy, confetti-like particles, a milestone message, and a direct choice: press **Enter**, **Space**, or **P** to continue, or press **Esc** to return to the menu. The 100-point milestone uses the stronger “Legendary Victory” message. Normal play also supports a pause overlay with resume controls through `P`, `Enter`, or `Space`.

## Architecture decision: Firebase Google Auth

Firebase Google Auth is not needed for the current offline Pygame release. The game has local high-score persistence and no user account, cloud save, or online leaderboard requirement. Adding authentication now would increase implementation and privacy complexity without improving the core experience.

Firebase should be introduced only if the product commits to cloud saves, cross-device profiles, verified leaderboards, account-based achievements, or opt-in remote analytics. The safe future architecture is an optional online mode using Firebase Authentication and Firestore. The desktop client may contain public Firebase client configuration, but it must never ship Admin SDK credentials or service-account secrets.

## Level-based world and event system

The game now changes its visual identity by level instead of showing one static background throughout the session. Levels 1–2 use a Calm Drizzle mood. Levels 3–4 introduce a Rainy Afternoon mood and gold drops. Levels 5–6 become a Thunderstorm with purple tint, thunder banners, lightning flashes, and rainbow drops. Level 7 and above become a Monsoon Surge with the strongest rain and event rhythm.

The scoring model is readable and matched to the visual language. Normal water drops award one point, gold drops award three points, and rainbow drops award five points before the active combo multiplier is applied. The HUD displays the active world name, the current level, the mission progress, and short event messages so the player always understands why the screen changed.

The event system is intentionally interactive but non-blocking. A lightning flash adds urgency without removing control. World transitions announce the next weather phase. Special-drop banners explain the exact reward. This keeps the game impressive while preserving the core skill of moving the tank and catching water.
