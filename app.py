import asyncio
import math
import app
import time
from events.input import BUTTON_TYPES, ButtonDownEvent, ButtonUpEvent
from tildagonos import tildagonos
from system.eventbus import eventbus
from app_components import clear_background
from system.patterndisplay.events import PatternDisable, PatternEnable

try:
    import settings
except ImportError:
    settings = None

try:
    import machine
except ImportError:
    machine = None

# Font Sizes Configurations
FONT_SIZE_TITLE = 20
FONT_SIZE_SUBTITLE = 12
FONT_SIZE_COLOR_LBL = 14
FONT_SIZE_NUMBER_LBL = 20
FONT_SIZE_COUNT = 48
FONT_SIZE_FORTUNE = 18  # Font size for the displayed fortune
FONT_SIZE_EXIT = 14


# 6 distinct bright colour themes, one colour per button.
# Each theme contains 6 highly distinct, contrasting colours.
# The daily seed picks which theme is active for the day.
THEMES = [
    # Theme 0 – PRIMARY FLIP
    [
        {"name": "RED",     "rgb": [255,   0,   0]},   # Button 1
        {"name": "GREEN",   "rgb": [  0, 230,  50]},   # Button 2
        {"name": "BLUE",    "rgb": [  0, 100, 255]},   # Button 3
        {"name": "YELLOW",  "rgb": [255, 230,   0]},   # Button 4
        {"name": "ORANGE",  "rgb": [255, 120,   0]},   # Button 5
        {"name": "PURPLE",  "rgb": [160,   0, 240]},   # Button 6
    ],
    # Theme 1 – NEON GLOW
    [
        {"name": "CYAN",    "rgb": [  0, 255, 255]},   # Button 1
        {"name": "MAGENTA", "rgb": [255,   0, 255]},   # Button 2
        {"name": "LIME",    "rgb": [ 50, 255,   0]},   # Button 3
        {"name": "ORANGE",  "rgb": [255, 140,   0]},   # Button 4
        {"name": "VIOLET",  "rgb": [140,   0, 255]},   # Button 5
        {"name": "YELLOW",  "rgb": [255, 255,   0]},   # Button 6
    ],
    # Theme 2 – RETRO ARCADE
    [
        {"name": "PINK",    "rgb": [255,  50, 150]},   # Button 1
        {"name": "TEAL",    "rgb": [  0, 200, 180]},   # Button 2
        {"name": "AMBER",   "rgb": [255, 180,   0]},   # Button 3
        {"name": "COBALT",  "rgb": [  0,  60, 255]},   # Button 4
        {"name": "RED",     "rgb": [240,   0,  50]},   # Button 5
        {"name": "MINT",    "rgb": [ 80, 240, 150]},   # Button 6
    ],
    # Theme 3 – TROPICAL WAVE
    [
        {"name": "CORAL",   "rgb": [255,  90,  60]},   # Button 1
        {"name": "TURQ",    "rgb": [  0, 220, 220]},   # Button 2
        {"name": "GOLD",    "rgb": [255, 200,   0]},   # Button 3
        {"name": "JUNGLE",  "rgb": [  0, 180,  60]},   # Button 4
        {"name": "ROSE",    "rgb": [255, 100, 180]},   # Button 5
        {"name": "INDIGO",  "rgb": [ 90,  30, 240]},   # Button 6
    ],
    # Theme 4 – CYBERPUNK
    [
        {"name": "PURPLE",  "rgb": [120,   0, 255]},   # Button 1
        {"name": "GREEN",   "rgb": [  0, 255, 100]},   # Button 2
        {"name": "RED",     "rgb": [255,  20,  50]},   # Button 3
        {"name": "BLUE",    "rgb": [  0, 200, 255]},   # Button 4
        {"name": "YELLOW",  "rgb": [255, 220,   0]},   # Button 5
        {"name": "MAGENTA", "rgb": [255,   0, 180]},   # Button 6
    ],
    # Theme 5 – FESTIVAL NIGHTS
    [
        {"name": "ROSE",    "rgb": [255,  20, 120]},   # Button 1
        {"name": "AQUA",    "rgb": [  0, 240, 200]},   # Button 2
        {"name": "FLAME",   "rgb": [255,  80,   0]},   # Button 3
        {"name": "VIOLET",  "rgb": [180,  30, 255]},   # Button 4
        {"name": "LIME",    "rgb": [150, 255,   0]},   # Button 5
        {"name": "SKY",     "rgb": [ 50, 150, 255]},   # Button 6
    ],
]

# COLORS will be set at runtime via _pick_daily_theme()
COLORS = THEMES[0]

BUTTON_NUM_TO_NAME = {
    1: "UP",
    2: "RIGHT",
    3: "CONFIRM",
    4: "DOWN",
    5: "LEFT",
    6: "CANCEL"
}
BUTTON_NAME_TO_NUM = {v: k for k, v in BUTTON_NUM_TO_NAME.items()}

# Seeded pseudo-random number generator (LCG)
class SeededRandom:
    def __init__(self, seed_val):
        self.state = seed_val & 0xFFFFFFFF
        if self.state == 0:
            self.state = 123456789

    def next_int(self):
        self.state = (self.state * 1103515245 + 12345) & 0x7FFFFFFF
        return self.state

    def choice(self, lst):
        if not lst:
            return None
        return lst[self.next_int() % len(lst)]

def get_unique_id():
    if machine and hasattr(machine, "unique_id"):
        try:
            uid = machine.unique_id()
            if uid:
                return uid
        except Exception:
            pass
    return b"tildagon_badge_fortune"

def get_current_date():
    try:
        t = time.localtime()
        return t[0], t[1], t[2]
    except Exception:
        return 2026, 6, 4

def make_daily_seed(badge_id, year, month, day):
    h = 5381
    for b in badge_id:
        h = ((h << 5) + h) + b
    h = ((h << 5) + h) + year
    h = ((h << 5) + h) + month
    h = ((h << 5) + h) + day
    return h & 0x7FFFFFFF

# Dictionary of fortunes
TEMPLATES = [
    ("[1] [2] will make you [3] [4].", 
     [["An unexpected", "A happy", "An ominous", "A chaotic", "A digital", "A mysterious", "A flashing", "A copper-plated"],
      ["surprise", "gift", "fact", "glitch", "solder joint", "frequency shift", "firmware update", "badge addon"],
      ["smile", "laugh", "confused", "question reality", "upgrade your firmware", "re-solder your life decisions"],
      ["today", "next week", "soon", "in a few days", "before the closing ceremony", "after the next power cut"]]),

    ("[1] will [2] [3].",
     [["You", "A loved one", "Your pet", "A friendly volunteer", "A rogue robot", "Your favorite badge"],
      ["go on", "return from", "embark on", "plan", "dream of"],
      ["an exciting adventure", "a long journey", "a trip to the shops", "a quest for rare components", "a midnight null sector run", "a quest for the perfect soldering flux"]]),

    ("Someone is going to [1] you a [2].",
     [["bring", "make", "solder", "debug for", "program for", "trade with"],
      ["delicious treat", "surprising discovery", "difficult truth", "custom PCB", "cold beverage", "rare electronic component"]]),

    ("Your luckiest number [1] is [2].",
     [["today", "this week", "this month", "for the rest of EMF", "in the null sector"],
      ["seven", "thirteen", "fourty-two", "eighty-eight", "one hundred and three", "0x4141", "1337", "65535"]]),

    ("You will [1] [2].",
     [["find", "discover", "reveal", "accidentally delete", "optimize"],
      ["something you thought you lost forever", "a hidden talent", "the answer to a question you've been asking", "a secret about yourself", "a hidden easter egg in the badge firmware", "a backdoor in the campsite network"]]),

    ("[1] goal you have will [2] [3].",
     [["A big", "The small", "A secret", "An ambitious", "A hardware-related"],
      ["come true", "materialise", "fail spectacularly but teach you a lot", "be completed"],
      ["today", "this week", "this month", "soon", "in a few days", "by tomorrow"]]),

    ("[1] is the perfect day to [2].",
     [["Today", "This week", "Tomorrow", "The final day of EMF"],
      ["try something new", "take a risk", "ask for help", "take a break", "start a new side project", "solder that tiny SMD chip", "sleep for 8 hours straight"]]),

    ("You will make a new [1] [2].",
     [["friend", "acquaintance", "nemesis", "ally", "co-conspirator", "badge partner"],
      ["very shortly", "at the bar", "at the null sector", "at Stage A", "at Stage B", "at Stage C", "at the arcade", "in the food queue"]]),

    ("You should volunteer at [1].",
     [["the bar", "the null sector", "Stage A", "Stage B", "Stage C", "the arcade", "the talks", "the workshops", "the information booth", "the badge tent", "the signal distribution hub"]]),

    ("A friendly robot at [1] will give you [2] [3].",
     [["the null sector", "the hackspace", "the arcade", "the badge tent", "the laser dome"],
      ["a mysterious PCB", "a glowing soda", "a helpful hint", "a components bag", "a deprecated microchip"],
      ["today", "tomorrow", "during the next talk", "under the cover of darkness"]]),

    ("You will find [1] in [2].",
     [["spiders", "inspiration for a new project", "spiders", "a lost USB drive", "the ultimate snack", "spiders", "a rogue LED", "an ancient floppy disk", "a duck"],
      ["the lounge", "the null sector", "a pile of cables", "Milliways", "a folding camp chair", "Maths Village"]]),

    ("A talk about [1] will inspire you to [2].",
     [["vintage computing", "amateur radio", "biotinkering", "lockpicking", "microcontrollers", "high-voltage art"],
      ["build a robot", "learn a new skill", "change your career", "stay up all night coding", "hack your badge", "design a hexpansion"]]),

    ("A midnight walk to [1] will reveal [2].",
     [["Stage A", "Milliways", "the Scottish Consulate", "the retro arcade", "the bar", "the quiet camp"],
      ["a beautiful constellation", "a secret DJ set", "a group of friendly hackers", "an unexpected art installation", "a lost robot searching for home"]]),

    ("Your code will [1] after you visit [2].",
     [["compile on the first try", "run twice as fast", "finally work", "magically fix itself", "stop throwing memory errors"],
      ["the coffee cart", "the bar", "the lounge", "Workshop C", "the hardware hacking village", "your local hacker village"]]),

    ("Beware of [1] near [2].",
     [["loose solder joints", "unsecured tents", "over-caffeinated volunteers", "high powered lasers", "roaming gps rave bots"],
      ["the main stage", "the null sector", "the campsite", "the food stands", "the radio antennas"]]),

    ("You should participate in [1].",
     [["a hacking contest", "a puzzle hunt", "a game tournament", "a soldering workshop"]])
]

def generate_fortune(seed_val):
    rng = SeededRandom(seed_val)
    template_data = rng.choice(TEMPLATES)
    template_str, options_list = template_data
    
    result = template_str
    for idx, options in enumerate(options_list):
        placeholder = f"[{idx + 1}]"
        choice = rng.choice(options)
        result = result.replace(placeholder, choice)
    return result

class FortuneTellerApp(app.App):
    def __init__(self):
        super().__init__()
        self.state = "COLOR_SELECTION"
        self.is_running = True
        self._render_update = None

        # Pick today's colour theme using the daily seed
        self._pick_daily_theme()
        
        # State variables
        self.selected_color_idx = 0
        self.selected_color_name = ""
        self.selected_color_rgb = [0, 0, 0]
        
        self.selected_number = 0
        self.visible_numbers = []
        self.fortune_text = ""
        
        # Animation variables
        self.anim_time = 0.0
        self.fold_duration = 1.0  # Each fold cycle lasts 1.0 second
        self.folds_count = 0
        self.folds_target = 0
        self.next_state_after_animation = "NUMBER_SELECTION"
        self.pressed_button = 1  # Track which button initiated the fold
        self.fold_base_angle = 0.0  # Running rotation offset for the folding animation
        
        # Exit/Cancel hold tracking
        self.cancel_is_held = False
        self.cancel_press_time = 0.0
        self.held_buttons = set()
        
        # Register events
        eventbus.on(ButtonDownEvent, self._handle_buttondown, self)
        eventbus.on(ButtonUpEvent, self._handle_buttonup, self)

    def _pick_daily_theme(self):
        """Select a theme from THEMES using today's daily seed."""
        global COLORS
        uid = get_unique_id()
        y, m, d = get_current_date()
        seed = make_daily_seed(uid, y, m, d)
        theme_idx = seed % len(THEMES)
        COLORS = THEMES[theme_idx]

    def minimise(self):
        from system.scheduler.events import RequestStopAppEvent
        eventbus.emit(RequestStopAppEvent(self))

    def _cleanup_all(self):
        self._clear_leds()
        self.held_buttons.clear()
        eventbus.remove(ButtonDownEvent, self._handle_buttondown, self)
        eventbus.remove(ButtonUpEvent, self._handle_buttonup, self)

    def _scale_color(self, color):
        brightness = 0.1
        if settings:
            try:
                b = settings.get("pattern_brightness")
                if b is not None:
                    brightness = b
            except Exception:
                pass
        return tuple(int(c * brightness) for c in color)

    def _get_button_leds(self, button_num):
        if button_num == 1:
            return [12, 1]
        else:
            idx = (button_num - 1) * 2
            return [idx, idx + 1]

    def _set_selection_leds(self):
        eventbus.emit(PatternDisable())
        for i in range(19):
            tildagonos.leds[i] = (0, 0, 0)
            
        for idx, color_info in enumerate(COLORS):
            btn_num = idx + 1
            scaled = self._scale_color(color_info["rgb"])
            led_indices = self._get_button_leds(btn_num)
            for led_idx in led_indices:
                tildagonos.leds[led_idx] = scaled
        tildagonos.leds.write()

    def _clear_leds(self):
        for i in range(19):
            tildagonos.leds[i] = (0, 0, 0)
        tildagonos.leds.write()
        eventbus.emit(PatternEnable())

    def _update_animation_leds(self):
        eventbus.emit(PatternDisable())
        for i in range(19):
            tildagonos.leds[i] = (0, 0, 0)
            
        scaled_color = self._scale_color(self.selected_color_rgb)
        
        # Determine progress within the current 1-second fold cycle
        p = (self.anim_time % self.fold_duration) / self.fold_duration
        step = int(p * 12) % 12
        
        # Index on ring based on pressed button
        idx_start = (self.pressed_button - 1) * 2
        
        # Animate outward in both directions
        idx_left = (idx_start - step) % 12
        idx_right = (idx_start + 1 + step) % 12
        
        led_left = 12 if idx_left == 0 else idx_left
        led_right = 12 if idx_right == 0 else idx_right
        
        tildagonos.leds[led_left] = scaled_color
        tildagonos.leds[led_right] = scaled_color
            
        tildagonos.leds.write()

    def _update_fortune_leds(self):
        eventbus.emit(PatternDisable())
        pulse = 0.5 + 0.5 * math.sin(time.ticks_ms() / 200.0)
        pulsed_rgb = [int(c * pulse) for c in self.selected_color_rgb]
        scaled_color = self._scale_color(pulsed_rgb)
        for i in range(1, 13):
            tildagonos.leds[i] = scaled_color
        tildagonos.leds.write()

    def _get_btn_num(self, event):
        for k, v in BUTTON_TYPES.items():
            if v in event.button:
                return BUTTON_NAME_TO_NUM.get(k)
        return None

    def _select_color(self, btn_num):
        self.pressed_button = btn_num
        self.selected_color_idx = btn_num - 1
        color_info = COLORS[self.selected_color_idx]
        self.selected_color_name = color_info["name"]
        self.selected_color_rgb = color_info["rgb"]
        
        self.folds_target = len(self.selected_color_name)
        self.folds_count = 0
        self.anim_time = 0.0
        self.fold_base_angle = 0.0  # Reset rotation for new fold sequence
        
        if self.folds_target % 2 == 0:
            self.visible_numbers = [2, 4, 6, 8, 10, 12]
        else:
            self.visible_numbers = [1, 3, 5, 7, 9, 11]
            
        self.state = "FOLDING_ANIMATION"
        self.next_state_after_animation = "NUMBER_SELECTION"

    def _select_number(self, btn_num):
        self.pressed_button = btn_num
        self.selected_number = self.visible_numbers[btn_num - 1]
        self.folds_target = self.selected_number
        self.folds_count = 0
        self.anim_time = 0.0
        self.fold_base_angle = 0.0  # Reset rotation for new fold sequence
        
        uid = get_unique_id()
        y, m, d = get_current_date()
        daily_seed = make_daily_seed(uid, y, m, d)
        path_seed = daily_seed + self.selected_color_idx * 17 + self.selected_number * 31
        self.fortune_text = generate_fortune(path_seed)
        
        self.state = "FOLDING_ANIMATION"
        self.next_state_after_animation = "FORTUNE_DISPLAY"

    def _handle_buttondown(self, event):
        btn_num = self._get_btn_num(event)
        if btn_num is None:
            return
            
        if btn_num in self.held_buttons:
            return
        self.held_buttons.add(btn_num)
        
        if btn_num == 6:
            if not self.cancel_is_held:
                self.cancel_is_held = True
                self.cancel_press_time = 0.0
            return # Delay processing button 6 (CANCEL/F) action until button UP to check for exit hold

        if self.state == "COLOR_SELECTION":
            self._select_color(btn_num)
        elif self.state == "NUMBER_SELECTION":
            self._select_number(btn_num)
        elif self.state == "FORTUNE_DISPLAY":
            self.state = "COLOR_SELECTION"
            self._set_selection_leds()

    def _handle_buttonup(self, event):
        btn_num = self._get_btn_num(event)
        if btn_num is not None:
            self.held_buttons.discard(btn_num)
            if btn_num == 6:
                duration = self.cancel_press_time
                self.cancel_is_held = False
                self.cancel_press_time = 0.0
                
                # If released quickly (less than 3 seconds), treat as normal button 6 press
                if duration < 3.0:
                    if self.state == "COLOR_SELECTION":
                        self._select_color(6)
                    elif self.state == "NUMBER_SELECTION":
                        self._select_number(6)
                    elif self.state == "FORTUNE_DISPLAY":
                        self.state = "COLOR_SELECTION"
                        self._set_selection_leds()

    def update(self, delta_ticks: float) -> bool:
        delta_seconds = delta_ticks / 1000.0
        
        if self.cancel_is_held:
            self.cancel_press_time += delta_seconds
            if self.cancel_press_time >= 3.0:
                self._cleanup_all()
                self.minimise()
                return True
                
        if self.state == "FOLDING_ANIMATION":
            self.anim_time += delta_seconds
            self._update_animation_leds()
            
            current_fold_index = int(self.anim_time / self.fold_duration)
            if current_fold_index >= self.folds_target:
                self.state = self.next_state_after_animation
                if self.state == "NUMBER_SELECTION":
                    scaled = self._scale_color(self.selected_color_rgb)
                    for i in range(1, 13):
                        tildagonos.leds[i] = scaled
                    tildagonos.leds.write()
                elif self.state == "FORTUNE_DISPLAY":
                    self._update_fortune_leds()
            return True
            
        elif self.state == "FORTUNE_DISPLAY":
            self._update_fortune_leds()
            return True
            
        return True

    def _draw_folding_animation(self, ctx):
        p = (self.anim_time % self.fold_duration) / self.fold_duration  # 0.0 to 1.0

        # Track which fold cycle we are on
        current_fold_index = int(self.anim_time / self.fold_duration)
        if current_fold_index > self.folds_target:
            current_fold_index = self.folds_target

        # Rotate by 30deg (pi / 6) per iteration. It stays constant during the
        # cover-and-reveal cycle and only updates when a new iteration starts.
        rotation_offset = current_fold_index * (math.pi / 6.0)

        # Smooth ease-in-out cubic scale
        # 1.0 = open (tips at outer radius), 0.0 = fully folded (tips at centre)
        sin_p = math.sin(p * math.pi)
        t_eased = 1.0 - math.pow(1.0 - sin_p, 3)  # Cubic cushion
        scale = 1.0 - t_eased

        ctx.save()
        clear_background(ctx)

        # Black background
        ctx.rgb(0.0, 0.0, 0.0)
        ctx.rectangle(-120, -120, 240, 240).fill()

        # Central character label
        label_fold_index = current_fold_index + 1
        if label_fold_index > self.folds_target:
            label_fold_index = self.folds_target

        if self.next_state_after_animation == "NUMBER_SELECTION":
            char_to_draw = self.selected_color_name[label_fold_index - 1]
        else:
            char_to_draw = str(label_fold_index)

        ctx.rgb(1.0, 1.0, 1.0)
        ctx.font_size = FONT_SIZE_COUNT
        ctx.text_align = ctx.CENTER
        ctx.text_baseline = ctx.MIDDLE
        ctx.move_to(0, 0).text(char_to_draw)

        # Folding triangles — rotated by rotation_offset so each iteration's tips
        # originate from the corners of the previous iteration's hexagon.
        rgb_float = tuple(c / 255.0 for c in self.selected_color_rgb)
        ctx.rgb(*rgb_float)
        R_outer = 150  # Enlarged to keep base edges outside the circular screen

        for i in range(6):
            # Base angle for this triangle, advanced by rotation_offset each fold
            theta_left = rotation_offset + i * math.pi / 3.0
            theta_right = theta_left + math.pi / 3.0
            theta_mid = (theta_left + theta_right) / 2.0

            # Tip travels from R_outer (open) to 0 (folded)
            r_tip = R_outer * scale
            x_tip = r_tip * math.cos(theta_mid)
            y_tip = r_tip * math.sin(theta_mid)

            ctx.begin_path()
            ctx.move_to(x_tip, y_tip)
            ctx.line_to(R_outer * math.cos(theta_left), R_outer * math.sin(theta_left))
            ctx.line_to(R_outer * math.cos(theta_right), R_outer * math.sin(theta_right))
            ctx.close_path()
            ctx.fill()

        ctx.restore()

    def _draw_color_selection(self, ctx):
        clear_background(ctx)
        
        # Title/Prompt in the center
        ctx.save()
        ctx.rgb(1.0, 1.0, 1.0)
        ctx.font_size = FONT_SIZE_TITLE
        ctx.text_align = ctx.CENTER
        ctx.text_baseline = ctx.MIDDLE
        ctx.move_to(0, -10).text("FORTUNE")
        ctx.move_to(0, 10).text("TELLER")
        ctx.font_size = FONT_SIZE_SUBTITLE
        ctx.rgb(0.7, 0.7, 0.7)
        ctx.move_to(0, 30).text("Press a color corner")
        ctx.move_to(0, 45).text("[Hold F to exit]")
        ctx.restore()
        
        # Draw color options radially
        R = 85
        for idx, color_info in enumerate(COLORS):
            btn_num = idx + 1
            theta = -math.pi / 2 + (btn_num - 1) * math.pi / 3
            x = R * math.cos(theta)
            y = R * math.sin(theta)
            
            ctx.save()
            ctx.translate(x, y)
            ctx.rotate(theta + math.pi / 2)
            
            rgb_float = tuple(c / 255.0 for c in color_info["rgb"])
            ctx.rgb(*rgb_float)
            ctx.text_align = ctx.CENTER
            ctx.text_baseline = ctx.MIDDLE
            ctx.font_size = FONT_SIZE_COLOR_LBL
            ctx.move_to(0, 0).text(color_info["name"])
            ctx.restore()

    def _draw_number_selection(self, ctx):
        clear_background(ctx)
        
        # Prompt in the center
        ctx.save()
        ctx.rgb(1.0, 1.0, 1.0)
        ctx.font_size = FONT_SIZE_TITLE
        ctx.text_align = ctx.CENTER
        ctx.text_baseline = ctx.MIDDLE
        ctx.move_to(0, -10).text("SELECT")
        ctx.move_to(0, 10).text("NUMBER")
        ctx.font_size = FONT_SIZE_SUBTITLE
        ctx.rgb(0.7, 0.7, 0.7)
        ctx.move_to(0, 30).text("Pick a flap number")
        ctx.restore()
        
        # Radial numbers matching the buttons
        R = 85
        for idx, num in enumerate(self.visible_numbers):
            btn_num = idx + 1
            theta = -math.pi / 2 + (btn_num - 1) * math.pi / 3
            x = R * math.cos(theta)
            y = R * math.sin(theta)
            
            ctx.save()
            ctx.translate(x, y)
            ctx.rotate(theta + math.pi / 2)
            
            rgb_float = tuple(c / 255.0 for c in self.selected_color_rgb)
            ctx.rgb(*rgb_float)
            ctx.text_align = ctx.CENTER
            ctx.text_baseline = ctx.MIDDLE
            ctx.font_size = FONT_SIZE_NUMBER_LBL
            ctx.move_to(0, 0).text(str(num))
            ctx.restore()

    def _draw_fortune_display(self, ctx):
        clear_background(ctx)
        
        # Pulse color circle in background or border
        ctx.save()
        rgb_float = tuple(c / 255.0 for c in self.selected_color_rgb)
        ctx.rgb(*rgb_float)
        ctx.line_width = 3
        ctx.arc(0, 0, 110, 0, 2 * math.pi, True).stroke()
        ctx.restore()
        
        # Fortune text in center
        ctx.save()
        ctx.rgb(1.0, 1.0, 1.0)
        ctx.font_size = FONT_SIZE_FORTUNE
        ctx.text_align = ctx.CENTER
        ctx.text_baseline = ctx.MIDDLE
        
        lines = self._wrap_text(self.fortune_text, ctx, 190)
        line_height = FONT_SIZE_FORTUNE + 2
        start_y = -((len(lines) - 1) * (line_height // 2))
        for idx, line in enumerate(lines):
            ctx.move_to(0, start_y + idx * line_height).text(line)
            
        # Tap to restart instruction
        ctx.rgb(0.6, 0.6, 0.6)
        ctx.font_size = FONT_SIZE_SUBTITLE
        ctx.move_to(0, 85).text("Press any button to retry")
        ctx.restore()

    def _wrap_text(self, text, ctx, max_width):
        words = text.split(" ")
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if ctx.text_width(test_line) <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines

    def draw(self, ctx):
        if self.state == "COLOR_SELECTION":
            self._draw_color_selection(ctx)
        elif self.state == "FOLDING_ANIMATION":
            self._draw_folding_animation(ctx)
        elif self.state == "NUMBER_SELECTION":
            self._draw_number_selection(ctx)
        elif self.state == "FORTUNE_DISPLAY":
            self._draw_fortune_display(ctx)
            
        # Draw hold-to-exit overlay
        if self.cancel_is_held and self.cancel_press_time >= 1.0:
            ctx.save()
            ctx.rgb(0.08, 0.08, 0.08)
            ctx.rectangle(-85, -30, 170, 60).fill()
            ctx.rgb(0.8, 0.2, 0.2)
            ctx.line_width = 1.5
            ctx.rectangle(-85, -30, 170, 60).stroke()
            
            ctx.rgb(1.0, 1.0, 1.0)
            ctx.font_size = FONT_SIZE_EXIT
            ctx.text_align = ctx.CENTER
            ctx.text_baseline = ctx.MIDDLE
            
            rem = max(1, int(4.0 - self.cancel_press_time))
            ctx.move_to(0, -10).text("Keep holding CANCEL")
            ctx.move_to(0, 10).text(f"to exit in {rem}s...")
            ctx.restore()

    async def run(self, render_update):
        self._render_update = render_update
        eventbus.emit(PatternDisable())
        self._set_selection_leds()
        
        last_time = time.ticks_ms()
        while self.is_running:
            cur_time = time.ticks_ms()
            delta_ticks = time.ticks_diff(cur_time, last_time)
            
            self.update(delta_ticks)
            await render_update()
            
            await asyncio.sleep(0.05)
            last_time = cur_time

__app_export__ = FortuneTellerApp
