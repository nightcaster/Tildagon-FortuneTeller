# Fortune Teller

A MicroPython application for the EMF 2024/2026 Tildagon Badge. This app emulates the classic paper origami fortune teller (cootie catcher) adapted for the hexagonal shape and 6 button corners of the Tildagon badge.

## How to Play

1. **Stage 1 (Select Color)**:
   - The badge selects one of **6 bright, multi-colour themes** for the day using a deterministic daily seed.
   - The 12 outer LEDs light up with the colours corresponding to each corner button.
   - Pressing a button triggers a folding animation that repeats $N$ times (where $N$ is the number of letters in the chosen color's name).
   - The screen draws a folding/unfolding hexagon that rotates by $30^\circ$ each fold iteration so the new flaps peel open from the creases of the previous fold (origami feel).

2. **Stage 2 (Select Number)**:
   - Depending on whether the folding count was odd or even, the screen displays a set of 6 numbers radially closest to the buttons (either odd numbers `[1, 3, 5, 7, 9, 11]` or even numbers `[2, 4, 6, 8, 10, 12]`).
   - Pressing a button triggers the folding animation $N$ times (where $N$ is the selected number).

3. **Stage 3 (Fortune)**:
   - Your daily fortune is displayed on the screen!
   - Fortunes are generated from a stable daily seed based on the current date and your badge's unique ID, so every day brings new predictions.
   - Press any button to restart or hold CANCEL (Button 6/F) for 3 seconds to exit.

## Development and Testing

Use the sync script `scripts/sync-badge.ps1` to upload files to a physical Tildagon badge using `mpremote` (creates the case-sensitive `:apps/FortuneTeller` folder).
