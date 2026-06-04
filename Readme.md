# Fortune Teller

A MicroPython application for the EMF 2024/2026 Tildagon Badge. This app emulates the classic paper origami fortune teller (cootie catcher) adapted for the hexagonal shape and 6 button corners of the Tildagon badge.

## How to Play

1. **Stage 1 (Select Color)**:
   - The 12 outer LEDs light up with colors representing each corner button:
     - **Button 1**: Red (3 letters)
     - **Button 2**: Orange (6 letters)
     - **Button 3**: Yellow (6 letters)
     - **Button 4**: Green (5 letters)
     - **Button 5**: Blue (4 letters)
     - **Button 6**: Magenta (7 letters)
   - Pressing a button triggers a folding animation that repeats $N$ times (where $N$ is the number of letters in the chosen color's name).
   - The screen draws a folding/unfolding hexagon, and the LEDs rotate.

2. **Stage 2 (Select Number)**:
   - Depending on whether the folding count was odd or even, the screen displays a set of 6 numbers radially closest to the buttons (either odd numbers `[1, 3, 5, 7, 9, 11]` or even numbers `[2, 4, 6, 8, 10, 12]`).
   - Pressing a button triggers the folding animation $N$ times (where $N$ is the selected number).

3. **Stage 3 (Fortune)**:
   - Your daily fortune is displayed on the screen!
   - Fortunes are generated from a stable daily seed based on the current date and your badge's unique ID, so every day brings new predictions.
   - Press any button to restart or CANCEL (Button 6/F) to exit.

## Development and Testing

Use the sync script `scripts/sync-badge.ps1` to upload files to a physical Tildagon badge using `mpremote`.
