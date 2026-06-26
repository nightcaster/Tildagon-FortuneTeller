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

## Template Syntax & Fortune Resolution

The application dynamically generates fortunes from templates (defined in `fortunes.py`) using a rule-based parser that handles grammar, plurality, and verb forms:

1. **Placeholders:** Basic tokens like `{CREATURE}` or `{MAP_LOCATION}` are randomly chosen from corresponding pools in the `TERMS` dictionary.
2. **Chaining (`+`):** Multiple tags can be chained together (e.g. `{PEOPLE_SUBJECT+HACKER_ADVERB+SOCIAL_VERB}`). The parser resolves each element left-to-right:
   - Adjectives can be placed before nouns (e.g. `{TECH_ADJECTIVE+TECH_ITEM}`).
   - Nouns resolved in the chain determine the overall subject plurality.
3. **Plurality Agreement:** 
   - Verb options are stored as pairs (e.g. `("trade with", "trades with")`).
   - Verbs resolved in a chain (or subsequent verb tags) automatically agree with the subject noun's plurality.
   - If a chain doesn't contain a subject noun (e.g. `{HACKER_ADVERB+SOCIAL_VERB}`), the verb falls back to agree with the most recently resolved noun.
4. **Modal Verbs:** If the verb (or chain containing a verb) is preceded by a modal or infinitive marker (such as `will`, `would`, `shall`, `should`, `can`, `could`, `may`, `might`, `must`, `to`), the parser automatically forces the verb into its infinitive/plural form (e.g. `"will quietly discover"` instead of `"will quietly discovers"`).
5. **Conditional Suffixes (`?`):** You can append conditional text based on the resolved tag's plurality, formatted as `{TAG?plural_suffix|singular_suffix}` (e.g. `{PEOPLE_SUBJECT?are coding late|is coding late}`).

## Development and Testing

Upload the application files (`app.py`, `fortunes.py`, `tildagon.toml`, `__init__.py`) to the case-sensitive `:apps/FortuneTeller` folder on the Tildagon badge (for example, using `mpremote fs cp`).


## Fortune Reviewer & Simulator

The project includes a Python-based local web simulator (`simulator.py`) designed for reviewing and validating the generated fortunes for any given seed.

### Features
* **Seed Controller:** Instantly inspect the outcomes of any base seed or generate a random seed.
* **Daily Seed Calculator:** Simulate your badge's Unique ID and any date to reproduce the exact 36 fortunes that would be generated on the badge for that day.
* **Dynamic Theme Highlighting:** Visualise which color theme is active (Theme 0 - 5) with a responsive user interface that automatically styles its panels to match active badge colors.
* **Dual View Mode:**
  * *Badge Paths (36 Fortunes)*: Shows the complete set of fortunes accessible by selecting any combination of the 6 color corners and 6 number flaps.
  * *Sequential List (100)*: Review 100 sequential fortunes starting from the base seed.
* **Filter Search:** Type keywords into the search bar to filter fortunes in real-time.
* **Markdown Export:** Export the complete generated fortune review report directly to your clipboard or download it as a markdown file.

### How to Run
Start the simulator server locally:
```powershell
python simulator.py
```
This will start a lightweight web server (defaults to port `8080`) and automatically open a new tab in your default web browser to the dashboard URL (`http://localhost:8080/`).

