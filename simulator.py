#!/usr/bin/env python3
import sys
import os
import urllib.parse
import json
import webbrowser
import http.server
import socket
import importlib
from datetime import datetime

# Add root folder to sys.path to find fortunes
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    import fortunes
except ImportError:
    print("Error: Could not import fortunes.py. Make sure you run the simulator from the folder containing fortunes.py")
    sys.exit(1)

# Themes definitions from app.py
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

def date_to_days(year, month, day):
    if month <= 2:
        month += 12
        year -= 1
    return 365 * year + year // 4 - year // 100 + year // 400 + (153 * month + 2) // 5 + day

def make_daily_seed(badge_id, year, month, day):
    if isinstance(badge_id, str):
        badge_id = badge_id.encode('utf-8')
    h = 5381
    for b in badge_id:
        h = ((h << 5) + h) + b
    h = ((h << 5) + h) + year
    h = ((h << 5) + h) + month
    h = ((h << 5) + h) + day
    return h & 0x7FFFFFFF

def pick_daily_theme(uid, y, m, d):
    """Select a theme from THEMES using today's daily seed, ensuring no repeats for 3 days."""
    if y < 2024:
        y = 2024
        
    d_epoch = date_to_days(2024, 1, 1)
    d_current = date_to_days(y, m, d)
    diff = max(0, d_current - d_epoch)
    
    # Base seed for the epoch
    if isinstance(uid, str):
        uid = uid.encode('utf-8')
    h = 5381
    for b in uid:
        h = ((h << 5) + h) + b
        
    recent = []
    for day_step in range(diff + 1):
        step_seed = (h + day_step) & 0x7FFFFFFF
        rng = fortunes.SeededRandom(step_seed)
        allowed = [idx for idx in range(len(THEMES)) if idx not in recent]
        theme_idx = rng.choice(allowed)
        recent.append(theme_idx)
        if len(recent) > 2:
            recent.pop(0)
            
    return recent[-1]

class SimulatorRequestHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress noise logs
        pass

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)
        
        if path == "/api/fortunes":
            self.handle_api_fortunes(query)
        elif path == "/api/config":
            self.handle_api_config()
        elif path == "/api/version":
            self.handle_api_version()
        elif path == "/":
            self.handle_home()
        else:
            self.send_error(404, "File not found")

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        if path == "/api/save":
            self.handle_api_save()
        else:
            self.send_error(404, "File not found")

    def handle_api_config(self):
        importlib.reload(fortunes)
        config_data = {
            "MAP_LOCATIONS": fortunes.MAP_LOCATIONS,
            "VILLAGES": fortunes.VILLAGES,
            "TERMS": fortunes.TERMS,
            "UPBEAT_TEMPLATES": fortunes.UPBEAT_TEMPLATES,
            "OMINOUS_TEMPLATES": fortunes.OMINOUS_TEMPLATES
        }
        response_bytes = json.dumps(config_data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(response_bytes)

    def handle_api_version(self):
        importlib.reload(fortunes)
        try:
            file_path = fortunes.__file__
            if file_path.endswith(".pyc"):
                file_path = file_path[:-1]
            mtime = os.path.getmtime(file_path)
        except Exception:
            mtime = 0
        response_bytes = json.dumps({"mtime": mtime}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(response_bytes)

    def handle_api_save(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        try:
            payload = json.loads(post_data.decode("utf-8"))
            map_locations = payload.get("MAP_LOCATIONS")
            villages = payload.get("VILLAGES")
            terms = payload.get("TERMS")
            upbeat_templates = payload.get("UPBEAT_TEMPLATES")
            ominous_templates = payload.get("OMINOUS_TEMPLATES")
            
            if (map_locations is None or villages is None or terms is None or 
                upbeat_templates is None or ominous_templates is None):
                raise ValueError("Missing required configuration fields")
                
            file_path = fortunes.__file__
            if file_path.endswith(".pyc"):
                file_path = file_path[:-1]
            elif file_path.endswith("__pycache__"):
                file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fortunes.py")
                
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("# fortunes.py\n")
                f.write("import math\n\n")
                f.write("# Seeded pseudo-random number generator (LCG) for deterministic selection\n")
                f.write("class SeededRandom:\n")
                f.write("    def __init__(self, seed_val):\n")
                f.write("        self.state = seed_val & 0xFFFFFFFF\n")
                f.write("        if self.state == 0:\n")
                f.write("            self.state = 123456789\n\n")
                f.write("    def next_int(self):\n")
                f.write("        self.state = (self.state * 1103515245 + 12345) & 0x7FFFFFFF\n")
                f.write("        return self.state\n\n")
                f.write("    def choice(self, lst):\n")
                f.write("        if not lst:\n")
                f.write("            return None\n")
                f.write("        return lst[self.next_int() % len(lst)]\n\n")
                
                f.write(f"MAP_LOCATIONS = {json.dumps(map_locations, indent=4)}\n\n")
                f.write(f"VILLAGES = {json.dumps(villages, indent=4)}\n\n")
                
                f.write("TERMS = {\n")
                f.write("    \"MAP_LOCATION\": MAP_LOCATIONS,\n")
                f.write("    \"VILLAGE\": VILLAGES,\n")
                f.write("    \"DESTINATION\": MAP_LOCATIONS + VILLAGES,\n")
                
                for k, v in terms.items():
                    if k in ("MAP_LOCATION", "VILLAGE", "DESTINATION"):
                        continue
                    f.write(f"    {json.dumps(k)}: [\n")
                    for item in v:
                        if isinstance(item, list):
                            tuple_str = ", ".join(json.dumps(x) for x in item)
                            f.write(f"        ({tuple_str}),\n")
                        else:
                            f.write(f"        {json.dumps(item)},\n")
                    f.write("    ],\n")
                f.write("}\n\n")
                
                f.write(f"UPBEAT_TEMPLATES = {json.dumps(upbeat_templates, indent=4)}\n\n")
                f.write(f"OMINOUS_TEMPLATES = {json.dumps(ominous_templates, indent=4)}\n\n")
                f.write("""def format_village(name, context_before):
    name_lower = name.lower().strip()
    proper_noun_exceptions = {"milliways", "bodgeham-on-wye", "glastonledburyshire-on-severn", "sheffield-by-the-sea"}
    if name_lower in proper_noun_exceptions:
        return f'"{name}"'
    self_descriptive_words = [
        "hackspace", "hacklab", "makespace", "makerspace", "make space", "maker space",
        "consulate", "embassy", "village", "sector", "camp", "lounge", "area", "house", 
        "room", "hq", "lab", "division", "station", "centre", "center", "ville"
    ]
    if any(word in name_lower for word in self_descriptive_words):
        return f'"{name}"'
    collective_nouns = ["club", "armada", "commission", "society", "project", "team", "group", "network", "force", "consortium", "union", "association", "friends", "bods", "racers", "pals", "gamers", "makers", "biohackers"]
    if any(name_lower.endswith(noun) for noun in collective_nouns):
        return f'the "{name}" village'
    return f'the village "{name}"'

def fix_a_an(text):
    vowels = "aeiouAEIOU"
    words = text.split(" ")
    for i in range(len(words) - 1):
        if words[i] == "a" or (i == 0 and words[i] == "A"):
            clean_next = words[i+1].lstrip("`\\\"'(")
            if clean_next and clean_next[0] in vowels:
                words[i] = "An" if words[i] == "A" else "an"
    return " ".join(words)

COLLECTIVE_PREFIXES = [
    "herd of",
    "gaggle of",
    "conference of",
    "swarm of",
    "parade of",
    "tsunami of",
    "mob of",
    "cabal of",
    "flock of"
]

def format_item(adjective, item, rng=None, no_collective=False):
    if isinstance(item, (list, tuple)):
        name = item[0]
        itype = item[1]
        unit = item[2] if len(item) > 2 else None
    else:
        name = item
        itype = "countable"
        unit = None

    if itype == "plural" and not unit and rng and not no_collective:
        if rng.next_int() % 2 == 0:
            unit = rng.choice(COLLECTIVE_PREFIXES)

    if unit:
        if adjective:
            phrase = f"{unit} {adjective} {name}"
        else:
            phrase = f"{unit} {name}"
        return fix_a_an(f"a {phrase}")
    else:
        if adjective:
            phrase = f"{adjective} {name}"
        else:
            phrase = name
        if itype == "countable":
            return fix_a_an(f"a {phrase}")
        return phrase

def choose_unique(rng, values, used_terms):
    available = [v for v in values if (v[0] if isinstance(v, (list, tuple)) else v) not in used_terms]
    if not available:
        available = values
    choice = rng.choice(available)
    raw = choice[0] if isinstance(choice, (list, tuple)) else choice
    used_terms.add(raw)
    return choice

def generate_fortune(seed_val):
    rng = SeededRandom(seed_val)
    
    vibe_roll = rng.next_int() % 100
    if vibe_roll < 85:
        template = rng.choice(UPBEAT_TEMPLATES)
    else:
        template = rng.choice(OMINOUS_TEMPLATES)
        
    result = template
    used_terms = set()

    # Resolve compound placeholders first
    while "{TECH_ADJECTIVE_ITEM}" in result:
        adj = choose_unique(rng, TERMS["TECH_ADJECTIVE"], used_terms)
        item = choose_unique(rng, TERMS["TECH_ITEM"], used_terms)
        val = format_item(adj, item, rng)
        result = result.replace("{TECH_ADJECTIVE_ITEM}", val, 1)

    while "{CRAFT_ADJECTIVE_ITEM}" in result:
        adj = choose_unique(rng, TERMS["CRAFT_ADJECTIVE"], used_terms)
        item = choose_unique(rng, TERMS["CRAFT_ITEM"], used_terms)
        val = format_item(adj, item, rng)
        result = result.replace("{CRAFT_ADJECTIVE_ITEM}", val, 1)

    while "{TECH_SHINY_ITEM}" in result:
        item = choose_unique(rng, TERMS["TECH_ITEM"], used_terms)
        val = format_item("shiny", item, rng)
        result = result.replace("{TECH_SHINY_ITEM}", val, 1)

    while "{TECH_RARE_ITEM}" in result:
        item = choose_unique(rng, TERMS["TECH_ITEM"], used_terms)
        val = format_item("rare", item, rng)
        result = result.replace("{TECH_RARE_ITEM}", val, 1)

    for key, values in TERMS.items():
        placeholders = []
        if key == "CREATURE_PLURAL":
            placeholders = [("{CREATURE_PLURAL}", True), ("{CREATURE_PLURAL_COLLECTIVE}", False)]
        elif key == "PEOPLE_SUBJECT":
            placeholders = [("{PEOPLE_SUBJECT}", True), ("{PEOPLE_SUBJECT_COLLECTIVE}", False)]
        else:
            placeholders = [("{" + key + "}", False)]
            
        for placeholder, no_coll in placeholders:
            while placeholder in result:
                choice = choose_unique(rng, values, used_terms)
                if key == "VILLAGE" or (key == "DESTINATION" and choice in VILLAGES):
                    idx = result.find(placeholder)
                    context_before = result[max(0, idx - 20):idx]
                    choice = format_village(choice, context_before)
                elif isinstance(choice, (list, tuple)):
                    choice = format_item("", choice, rng, no_collective=no_coll)
                    
                result = result.replace(placeholder, choice, 1)
            
    if result:
        result = result[0].upper() + result[1:]
        result = fix_a_an(result)
    return result

def generate_fortune_metadata(seed_val):
    rng = SeededRandom(seed_val)
    
    vibe_roll = rng.next_int() % 100
    if vibe_roll < 85:
        template = rng.choice(UPBEAT_TEMPLATES)
        vibe = "upbeat"
    else:
        template = rng.choice(OMINOUS_TEMPLATES)
        vibe = "ominous"
        
    tokens = [{"type": "text", "value": template}]
    used_terms = set()

    # Helper to resolve compound placeholders in tokens list
    def replace_compound_placeholder(placeholder, key_name, adj_source, item_source, fixed_adj=None):
        while True:
            found_idx = -1
            for idx, token in enumerate(tokens):
                if token["type"] == "text" and placeholder in token["value"]:
                    found_idx = idx
                    break
            if found_idx == -1:
                break
                
            adj = fixed_adj if fixed_adj is not None else choose_unique(rng, adj_source, used_terms)
            item = choose_unique(rng, item_source, used_terms)
            
            formatted_val = format_item(adj, item, rng)
            raw_val = item[0] if isinstance(item, (list, tuple)) else item
            
            token_text = tokens[found_idx]["value"]
            split_idx = token_text.find(placeholder)
            left_text = token_text[:split_idx]
            right_text = token_text[split_idx + len(placeholder):]
            
            new_tokens = []
            if left_text:
                new_tokens.append({"type": "text", "value": left_text})
            new_tokens.append({
                "type": "term",
                "key": key_name,
                "value": formatted_val,
                "raw_value": raw_val,
                "adj": adj
            })
            if right_text:
                new_tokens.append({"type": "text", "value": right_text})
                
            tokens[found_idx:found_idx+1] = new_tokens

    replace_compound_placeholder("{TECH_ADJECTIVE_ITEM}", "TECH_ITEM", TERMS["TECH_ADJECTIVE"], TERMS["TECH_ITEM"])
    replace_compound_placeholder("{CRAFT_ADJECTIVE_ITEM}", "CRAFT_ITEM", TERMS["CRAFT_ADJECTIVE"], TERMS["CRAFT_ITEM"])
    replace_compound_placeholder("{TECH_SHINY_ITEM}", "TECH_ITEM", None, TERMS["TECH_ITEM"], "shiny")
    replace_compound_placeholder("{TECH_RARE_ITEM}", "TECH_ITEM", None, TERMS["TECH_ITEM"], "rare")

    for key, values in TERMS.items():
        placeholders = []
        if key == "CREATURE_PLURAL":
            placeholders = [("{CREATURE_PLURAL}", True), ("{CREATURE_PLURAL_COLLECTIVE}", False)]
        elif key == "PEOPLE_SUBJECT":
            placeholders = [("{PEOPLE_SUBJECT}", True), ("{PEOPLE_SUBJECT_COLLECTIVE}", False)]
        else:
            placeholders = [("{" + key + "}", False)]
            
        for placeholder, no_coll in placeholders:
            while True:
                found_idx = -1
                for idx, token in enumerate(tokens):
                    if token["type"] == "text" and placeholder in token["value"]:
                        found_idx = idx
                        break
                if found_idx == -1:
                    break
                    
                choice = choose_unique(rng, values, used_terms)
                raw_choice = choice[0] if isinstance(choice, (list, tuple)) else choice
                
                if key == "VILLAGE" or (key == "DESTINATION" and choice in VILLAGES):
                    full_text_before = ""
                    for i in range(found_idx):
                        full_text_before += tokens[i]["value"]
                    token_text = tokens[found_idx]["value"]
                    split_idx = token_text.find(placeholder)
                    full_text_before += token_text[:split_idx]
                    
                    context_before = full_text_before[max(0, len(full_text_before) - 20):]
                    choice = format_village(choice, context_before)
                elif isinstance(choice, (list, tuple)):
                    choice = format_item("", choice, rng, no_collective=no_coll)
                    
                token_text = tokens[found_idx]["value"]
                split_idx = token_text.find(placeholder)
                left_text = token_text[:split_idx]
                right_text = token_text[split_idx + len(placeholder):]
                
                new_tokens = []
                if left_text:
                    new_tokens.append({"type": "text", "value": left_text})
                new_tokens.append({
                    "type": "term",
                    "key": key,
                    "value": choice,
                    "raw_value": raw_choice,
                    "adj": "",
                    "no_collective": no_coll
                })
                if right_text:
                    new_tokens.append({"type": "text", "value": right_text})
                    
                tokens[found_idx:found_idx+1] = new_tokens

    if tokens and tokens[0]["value"]:
        val = tokens[0]["value"]
        tokens[0]["value"] = val[0].upper() + val[1:]
        
    vowels = "aeiouAEIOU"
    
    def get_next_word(start_idx):
        for j in range(start_idx, len(tokens)):
            val = tokens[j]["value"]
            words = val.split()
            if words:
                return words[0].lstrip("`\\\"'(")
        return ""

    for i in range(len(tokens)):
        token = tokens[i]
        if token["type"] == "text":
            val = token["value"]
            parts = val.split(" ")
            changed = False
            for p_idx in range(len(parts)):
                word = parts[p_idx]
                if word == "a" or (word == "A" and i == 0 and p_idx == 0):
                    next_w = ""
                    if p_idx + 1 < len(parts):
                        for k in range(p_idx + 1, len(parts)):
                            if parts[k]:
                                next_w = parts[k].lstrip("`\\\"'(")
                                break
                    if not next_w:
                        next_w = get_next_word(i + 1)
                        
                    if next_w and next_w[0] in vowels:
                        parts[p_idx] = "An" if word == "A" else "an"
                        changed = True
            if changed:
                token["value"] = " ".join(parts)

    return {
        "template": template,
        "vibe": vibe,
        "tokens": tokens
    }

def get_word_value(word):
    total = 0
    word = word.upper()
    for idx, char in enumerate(word):
        if 'A' <= char <= 'Z':
            val = ord(char) - ord('A') + 1
            if idx == len(word) - 1:
                total += val * 26
            else:
                total += val
    return total
""")
            importlib.reload(fortunes)
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode("utf-8"))
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode("utf-8"))

    def handle_api_fortunes(self, query):
        importlib.reload(fortunes)
        badge_id = query.get("badge_id", ["tildagon_badge_fortune"])[0]
        
        # Get date
        date_str = query.get("date", [""])[0]
        if date_str:
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                year, month, day = dt.year, dt.month, dt.day
            except Exception:
                now = datetime.now()
                year, month, day = now.year, now.month, now.day
        else:
            now = datetime.now()
            year, month, day = now.year, now.month, now.day
            
        # Resolved base seed
        if "seed" in query:
            try:
                base_seed = int(query["seed"][0])
            except ValueError:
                base_seed = make_daily_seed(badge_id, year, month, day)
        else:
            base_seed = make_daily_seed(badge_id, year, month, day)
            
        # Determine theme
        if "theme_idx" in query and query["theme_idx"][0].isdigit():
            theme_idx = int(query["theme_idx"][0]) % len(THEMES)
            theme_mode = "manual"
        else:
            theme_idx = pick_daily_theme(badge_id, year, month, day)
            theme_mode = "auto"
            
        colors = THEMES[theme_idx]
        
        # 2. Generate the 36 badge path fortunes
        paths = []
        for color_idx, color_info in enumerate(colors):
            color_name = color_info["name"]
            color_rgb = color_info["rgb"]
            
            # Determine visible numbers for this color
            if len(color_name) % 2 == 0:
                visible_numbers = [2, 4, 6, 8, 10, 12]
            else:
                visible_numbers = [1, 3, 5, 7, 9, 11]
                
            for number in visible_numbers:
                # Same formula as app.py
                word_val = fortunes.get_word_value(color_name)
                path_seed = base_seed + word_val + number * 31
                metadata = fortunes.generate_fortune_metadata(path_seed)
                fortune_text = "".join(t["value"] for t in metadata["tokens"])
                paths.append({
                    "color_idx": color_idx,
                    "color_name": color_name,
                    "color_rgb": color_rgb,
                    "number": number,
                    "path_seed": path_seed,
                    "fortune": fortune_text,
                    "tokens": metadata["tokens"],
                    "template": metadata["template"],
                    "vibe": metadata["vibe"]
                })
                
        # 3. Generate sequential random fortunes from seed
        sequential = []
        seq_rng = fortunes.SeededRandom(base_seed)
        for i in range(100):
            step_seed = seq_rng.next_int()
            metadata = fortunes.generate_fortune_metadata(step_seed)
            fortune_text = "".join(t["value"] for t in metadata["tokens"])
            sequential.append({
                "index": i + 1,
                "seed": step_seed,
                "fortune": fortune_text,
                "tokens": metadata["tokens"],
                "template": metadata["template"],
                "vibe": metadata["vibe"]
            })
            
        response_data = {
            "seed": base_seed,
            "theme_idx": theme_idx,
            "theme_mode": theme_mode,
            "theme_colors": colors,
            "badge_id": badge_id,
            "date": f"{year:04d}-{month:02d}-{day:02d}",
            "paths": paths,
            "sequential": sequential
        }
        
        response_bytes = json.dumps(response_data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(response_bytes)

    def handle_home(self):
        html_content = HTML_TEMPLATE
        response_bytes = html_content.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)

def find_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔮 Tildagon Fortune Teller Reviewer & Editor</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Plus+Jakarta+Sans:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-gradient: linear-gradient(135deg, #0f0c20 0%, #15102a 50%, #06020f 100%);
            --panel-bg: rgba(255, 255, 255, 0.03);
            --panel-border: rgba(255, 255, 255, 0.08);
            --panel-border-hover: rgba(255, 255, 255, 0.16);
            --text-primary: #f8f7ff;
            --text-secondary: #a09cb0;
            --accent-cyan: #00f0ff;
            --accent-purple: #c000ff;
            --font-display: 'Outfit', sans-serif;
            --font-sans: 'Plus Jakarta Sans', sans-serif;

            /* Dyn variables, will be updated by JS */
            --theme-color-0: #ff0000;
            --theme-color-1: #00ff00;
            --theme-color-2: #0000ff;
            --theme-color-3: #ffff00;
            --theme-color-4: #ff00ff;
            --theme-color-5: #00ffff;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: var(--font-sans);
            background: var(--bg-gradient);
            background-attachment: fixed;
            color: var(--text-primary);
            min-height: 100vh;
            padding: 2rem 1.5rem;
            line-height: 1.5;
            overflow-y: scroll;
        }

        /* Container */
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        /* Glassmorphism utility card */
        .glass-card {
            background: var(--panel-bg);
            border: 1px solid var(--panel-border);
            border-radius: 16px;
            padding: 1.5rem;
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .glass-card:hover {
            border-color: var(--panel-border-hover);
        }

        /* Header */
        header {
            margin-bottom: 2rem;
            text-align: center;
        }

        header h1 {
            font-family: var(--font-display);
            font-size: 2.8rem;
            font-weight: 800;
            letter-spacing: -1px;
            background: linear-gradient(90deg, var(--accent-cyan), #a154ff, var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            display: inline-flex;
            align-items: center;
            gap: 0.75rem;
        }

        header p {
            color: var(--text-secondary);
            font-size: 1.1rem;
            max-width: 600px;
            margin: 0 auto;
        }

        /* Dashboard Grid */
        .dashboard-grid {
            display: grid;
            grid-template-columns: 350px 1fr;
            gap: 1.5rem;
            align-items: start;
        }

        @media (max-width: 1024px) {
            .dashboard-grid {
                grid-template-columns: 1fr;
            }
        }

        /* Sidebar Controls */
        .sidebar {
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }

        .sidebar-section h2 {
            font-family: var(--font-display);
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 1rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            padding-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        /* Forms */
        .form-group {
            margin-bottom: 1rem;
        }

        .form-group label {
            display: block;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-secondary);
            margin-bottom: 0.5rem;
            font-weight: 600;
        }

        .input-control {
            width: 100%;
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 8px;
            padding: 0.75rem 1rem;
            color: #fff;
            font-family: var(--font-sans);
            font-size: 1rem;
            transition: all 0.2s ease;
        }

        .input-control:focus {
            outline: none;
            border-color: var(--accent-cyan);
            box-shadow: 0 0 10px rgba(0, 240, 255, 0.2);
        }

        .button-group {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.5rem;
            margin-top: 0.5rem;
        }

        .btn {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            color: var(--text-primary);
            padding: 0.6rem 1rem;
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }

        .btn:hover {
            background: rgba(255, 255, 255, 0.15);
            border-color: rgba(255, 255, 255, 0.25);
            transform: translateY(-1px);
        }

        .btn-accent {
            background: linear-gradient(135deg, rgba(0, 240, 255, 0.2) 0%, rgba(192, 0, 255, 0.2) 100%);
            border: 1px solid rgba(0, 240, 255, 0.4);
        }

        .btn-accent:hover {
            background: linear-gradient(135deg, rgba(0, 240, 255, 0.35) 0%, rgba(192, 0, 255, 0.35) 100%);
            border-color: var(--accent-cyan);
            box-shadow: 0 0 15px rgba(0, 240, 255, 0.3);
        }

        /* Active Theme Colors visualization */
        .color-palette-bar {
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: 6px;
            margin-top: 1rem;
        }

        .color-dot {
            height: 32px;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: var(--font-display);
            font-size: 0.75rem;
            font-weight: 700;
            text-shadow: 0 1px 2px rgba(0,0,0,0.8);
            border: 1px solid rgba(255,255,255,0.1);
        }

        /* Tabs and Controls */
        .results-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
            margin-bottom: 1.5rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            padding-bottom: 1rem;
        }

        .tabs {
            display: flex;
            gap: 0.5rem;
            background: rgba(0, 0, 0, 0.3);
            padding: 4px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        .tab-btn {
            background: transparent;
            border: none;
            padding: 0.5rem 1.25rem;
            border-radius: 8px;
            color: var(--text-secondary);
            font-family: var(--font-sans);
            font-weight: 600;
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .tab-btn.active {
            background: rgba(255, 255, 255, 0.08);
            color: var(--text-primary);
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
        }

        .toolbar {
            display: flex;
            gap: 0.75rem;
            align-items: center;
            flex-grow: 1;
            max-width: 400px;
            justify-content: flex-end;
        }

        .search-container {
            position: relative;
            flex-grow: 1;
        }

        .search-input {
            width: 100%;
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 0.5rem 1rem 0.5rem 2.25rem;
            color: #fff;
            font-size: 0.9rem;
        }

        .search-input:focus {
            outline: none;
            border-color: var(--accent-cyan);
        }

        .search-icon {
            position: absolute;
            left: 0.75rem;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-secondary);
            pointer-events: none;
            font-size: 0.9rem;
        }

        /* Path Grid Layout */
        .colors-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
            gap: 1.5rem;
        }

        .color-card {
            border-radius: 12px;
            border: 1px solid var(--border-color);
            background: linear-gradient(180deg, var(--bg-alpha) 0%, rgba(255,255,255,0.01) 100%);
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }

        .color-card-header {
            padding: 1rem;
            font-family: var(--font-display);
            font-weight: 800;
            font-size: 1.15rem;
            letter-spacing: 0.5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border-color);
            background: rgba(0, 0, 0, 0.2);
        }

        .color-pill {
            padding: 0.2rem 0.6rem;
            border-radius: 20px;
            font-size: 0.7rem;
            text-transform: uppercase;
            font-weight: 700;
            letter-spacing: 1px;
            border: 1px solid rgba(255,255,255,0.15);
        }

        .fortunes-list {
            padding: 1rem;
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
            flex-grow: 1;
        }

        .fortune-item {
            background: rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            padding: 0.75rem;
            display: flex;
            gap: 0.75rem;
            align-items: flex-start;
            transition: all 0.2s ease;
        }

        .fortune-item:hover {
            border-color: rgba(255, 255, 255, 0.15);
            background: rgba(255, 255, 255, 0.02);
            transform: scale(1.01);
        }

        .fortune-number {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: var(--btn-color);
            color: #fff;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: var(--font-display);
            font-weight: 800;
            font-size: 0.9rem;
            flex-shrink: 0;
            box-shadow: 0 0 10px rgba(0,0,0,0.3);
            text-shadow: 0 1px 2px rgba(0,0,0,0.6);
        }

        .fortune-text-box {
            display: flex;
            flex-direction: column;
            gap: 4px;
            flex-grow: 1;
        }

        .fortune-text {
            font-size: 0.95rem;
            font-weight: 400;
            color: #fff;
        }

        .fortune-meta {
            font-size: 0.75rem;
            color: var(--text-secondary);
            font-family: monospace;
        }

        /* Sequential view list */
        .seq-list {
            display: grid;
            grid-template-columns: 1fr;
            gap: 0.75rem;
            max-height: 70vh;
            overflow-y: auto;
            padding-right: 0.5rem;
        }

        .seq-item {
            background: rgba(0,0,0,0.2);
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 8px;
            padding: 1rem;
            display: flex;
            gap: 1rem;
            align-items: center;
            transition: all 0.2s ease;
        }

        .seq-item:hover {
            border-color: rgba(255, 255, 255, 0.15);
            background: rgba(255,255,255,0.02);
        }

        .seq-badge {
            font-family: var(--font-display);
            font-size: 1rem;
            font-weight: 800;
            color: var(--accent-cyan);
            width: 48px;
            text-align: right;
            border-right: 1px solid rgba(255,255,255,0.1);
            padding-right: 0.75rem;
            flex-shrink: 0;
        }

        .seq-content {
            flex-grow: 1;
        }

        .seq-seed {
            font-family: monospace;
            font-size: 0.75rem;
            color: var(--text-secondary);
            margin-top: 4px;
        }

        /* Theme index grid */
        .theme-grid {
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: 4px;
        }

        .theme-select-btn {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 6px;
            color: var(--text-secondary);
            padding: 0.4rem;
            font-size: 0.8rem;
            font-weight: 600;
            cursor: pointer;
            text-align: center;
        }

        .theme-select-btn.active {
            background: var(--accent-purple);
            color: #fff;
            border-color: var(--accent-cyan);
            box-shadow: 0 0 10px rgba(192, 0, 255, 0.4);
        }

        /* Toggle switches */
        .switch-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 0.75rem;
        }

        .switch-label {
            font-size: 0.85rem;
            color: var(--text-secondary);
        }

        .switch {
            position: relative;
            display: inline-block;
            width: 46px;
            height: 24px;
        }

        .switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }

        .slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: rgba(255,255,255,0.1);
            transition: .3s;
            border-radius: 34px;
            border: 1px solid rgba(255,255,255,0.1);
        }

        .slider:before {
            position: absolute;
            content: "";
            height: 16px;
            width: 16px;
            left: 3px;
            bottom: 3px;
            background-color: white;
            transition: .3s;
            border-radius: 50%;
        }

        input:checked + .slider {
            background-color: var(--accent-cyan);
        }

        input:checked + .slider:before {
            transform: translateX(22px);
        }

        /* Footer styling */
        footer {
            margin-top: 3rem;
            text-align: center;
            font-size: 0.8rem;
            color: var(--text-secondary);
            border-top: 1px solid rgba(255,255,255,0.05);
            padding-top: 1.5rem;
        }

        /* Search highlights */
        .hidden {
            display: none !important;
        }

        .highlight {
            background: rgba(0, 240, 255, 0.25);
            color: #fff;
            border-radius: 2px;
        }

        /* Custom Scrollbar for list container */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.02);
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.15);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(255, 255, 255, 0.3);
        }

        /* Loading indicator overlay */
        .loader-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(10, 6, 26, 0.7);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10;
            border-radius: 16px;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.2s ease;
            font-family: var(--font-display);
            font-weight: 600;
            color: var(--accent-cyan);
            gap: 0.5rem;
        }

        .loader-overlay.active {
            opacity: 1;
            pointer-events: auto;
        }

        .spinner {
            width: 24px;
            height: 24px;
            border: 3px solid rgba(0, 240, 255, 0.2);
            border-top-color: var(--accent-cyan);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        /* Term tokens color coding styling */
        .term-token {
            display: inline-block;
            padding: 0.05rem 0.3rem;
            border-radius: 4px;
            font-weight: 600;
            cursor: pointer;
            border: 1px solid rgba(255,255,255,0.06);
            transition: all 0.15s ease;
            margin: 0 1px;
        }
        .term-token:hover {
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.5);
            border-color: rgba(255,255,255,0.25);
        }

        .term-key-MAP_LOCATION { background: rgba(255, 99, 132, 0.15); color: rgb(255, 120, 150); }
        .term-key-VILLAGE { background: rgba(255, 206, 86, 0.15); color: rgb(255, 220, 100); }
        .term-key-DESTINATION { background: rgba(255, 159, 64, 0.15); color: rgb(255, 180, 100); }
        .term-key-PEOPLE_SUBJECT { background: rgba(75, 192, 192, 0.15); color: rgb(100, 220, 220); }
        .term-key-CREATURE_SUBJECT { background: rgba(54, 162, 235, 0.15); color: rgb(100, 190, 255); }
        .term-key-CREATURE_PLURAL { background: rgba(54, 162, 235, 0.15); color: rgb(100, 190, 255); }
        .term-key-TECH_VERB { background: rgba(153, 102, 255, 0.15); color: rgb(180, 140, 255); }
        .term-key-SOCIAL_VERB { background: rgba(201, 203, 207, 0.15); color: rgb(220, 220, 220); }
        .term-key-ACTIVE_DEVICE { background: rgba(233, 30, 99, 0.15); color: rgb(255, 100, 150); }
        .term-key-BENCH_TOOL { background: rgba(156, 39, 176, 0.15); color: rgb(220, 100, 255); }
        .term-key-TECH_TARGET { background: rgba(0, 150, 136, 0.15); color: rgb(50, 220, 200); }
        .term-key-SOCIAL_OBJECT { background: rgba(33, 150, 243, 0.15); color: rgb(100, 180, 255); }
        .term-key-ABSURD_OBJECT { background: rgba(255, 235, 59, 0.15); color: rgb(255, 240, 100); }
        .term-key-CAMP_ACTION { background: rgba(76, 175, 80, 0.15); color: rgb(120, 230, 120); }
        .term-key-HACKER_ACTION { background: rgba(139, 195, 74, 0.15); color: rgb(180, 240, 120); }
        .term-key-HAZARD { background: rgba(244, 67, 54, 0.15); color: rgb(255, 120, 120); }
        .term-key-ADJECTIVE { background: rgba(255, 193, 7, 0.15); color: rgb(255, 210, 80); }
        .term-key-ITEM { background: rgba(255, 87, 34, 0.15); color: rgb(255, 130, 90); }
        .term-key-TECH_TRIVIA { background: rgba(103, 58, 183, 0.15); color: rgb(160, 120, 255); }
        .term-key-TIME { background: rgba(96, 125, 139, 0.15); color: rgb(160, 180, 190); }
        .term-key-LUCKY_NUMBER { background: rgba(0, 188, 212, 0.15); color: rgb(100, 230, 255); }

        /* Modal/Popover CSS */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(10, 6, 26, 0.8);
            backdrop-filter: blur(8px);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 100;
            opacity: 1;
            transition: opacity 0.2s ease;
        }
        .modal-overlay.hidden {
            opacity: 0;
            pointer-events: none;
        }
        .modal-content {
            width: 90%;
            max-width: 550px;
            max-height: 85vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            padding: 1.5rem;
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            padding-bottom: 0.5rem;
        }
        .modal-close {
            background: transparent;
            border: none;
            color: var(--text-secondary);
            font-size: 1.5rem;
            cursor: pointer;
        }
        .modal-body {
            overflow-y: auto;
            flex-grow: 1;
        }
        .modal-options-list {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            max-height: 300px;
            overflow-y: auto;
            background: rgba(0,0,0,0.3);
            padding: 0.75rem;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.05);
            margin-top: 0.5rem;
        }
        .modal-option-item {
            font-size: 0.9rem;
            padding: 0.5rem 0.75rem;
            border-radius: 6px;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.06);
            cursor: pointer;
            transition: all 0.15s ease;
            white-space: normal;
            word-break: break-word;
            line-height: 1.4;
        }
        .modal-option-item:hover {
            background: rgba(255,255,255,0.08);
            border-color: rgba(255,255,255,0.15);
        }
        .modal-option-item.active {
            border-color: var(--accent-cyan);
            background: rgba(0, 240, 255, 0.1);
            color: #fff;
            font-weight: 600;
        }

        /* Dictionary & Templates Editor CSS */
        .dictionary-view {
            display: grid;
            grid-template-columns: 1fr;
            gap: 1.5rem;
        }
        .dict-category-card {
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 12px;
            background: rgba(255,255,255,0.02);
            padding: 1.25rem;
        }
        .dict-category-title {
            font-family: var(--font-display);
            font-size: 1.2rem;
            font-weight: 600;
            color: var(--accent-cyan);
            margin-bottom: 0.75rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .dict-terms-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 0.5rem;
            max-height: 550px;
            overflow-y: auto;
            padding-right: 0.5rem;
            margin-top: 1rem;
        }
        .dict-term-editable {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            background: rgba(0,0,0,0.3);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 8px;
            padding: 0.5rem 0.75rem;
        }
        .dict-term-input {
            background: transparent;
            border: none;
            color: #fff;
            font-family: var(--font-sans);
            font-size: 0.85rem;
            flex-grow: 1;
            width: 100%;
        }
        .dict-term-input:focus {
            outline: none;
            border-bottom: 1px solid var(--accent-cyan);
        }
        .dict-term-del {
            background: transparent;
            border: none;
            color: var(--text-secondary);
            cursor: pointer;
            font-size: 1rem;
            padding: 0 0.25rem;
        }
        .dict-term-del:hover {
            color: rgb(255, 100, 100);
        }

        .template-item-row {
            display: flex;
            gap: 0.5rem;
            background: rgba(0,0,0,0.3);
            padding: 0.75rem;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.05);
            align-items: center;
        }
        .template-textarea {
            background: transparent;
            border: none;
            color: #fff;
            font-family: var(--font-sans);
            font-size: 0.9rem;
            width: 100%;
            resize: vertical;
            min-height: 40px;
        }
        .template-textarea:focus {
            outline: none;
            border-bottom: 1px solid var(--accent-cyan);
        }
        .adj-tab-btn {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 6px;
            color: var(--text-secondary);
            padding: 0.35rem 0.75rem;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .adj-tab-btn.active {
            background: var(--accent-cyan);
            color: #000;
            border-color: var(--accent-cyan);
            box-shadow: 0 0 10px rgba(0, 240, 255, 0.3);
        }
        .adj-tab-btn-add {
            border-style: dashed;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header>
            <h1>🔮 Tildagon Fortune Teller Reviewer & Editor</h1>
            <p>Seeded Fortune Generator & Simulator. Color-coded terms, interactive dictionaries, real-time template editing, and instant updates.</p>
            <p style="margin-top: 0.5rem; font-size: 1.15rem; font-family: var(--font-display);"><span id="stat-total-fortunes" style="color: var(--accent-cyan); font-weight: 700;">Calculating...</span> possible unique fortunes in total database pool</p>
        </header>

        <!-- Main Workspace -->
        <div class="dashboard-grid">
            
            <!-- Controls Sidebar -->
            <div class="sidebar">
                
                <!-- Main Seed Control -->
                <div class="glass-card sidebar-section">
                    <h2>Seed Controller</h2>
                    
                    <div class="form-group">
                        <label for="input-seed">Base Seed</label>
                        <input type="number" id="input-seed" class="input-control" value="0">
                        <div class="button-group">
                            <button class="btn" id="btn-random-seed">🎲 Random</button>
                            <button class="btn btn-accent" id="btn-today-seed">📅 Today</button>
                        </div>
                    </div>
                </div>

                <!-- Date & Badge Calculator -->
                <div class="glass-card sidebar-section">
                    <h2>Daily Seed Calculator</h2>
                    
                    <div class="form-group">
                        <label for="input-badge-id">Badge Unique ID</label>
                        <input type="text" id="input-badge-id" class="input-control" value="tildagon_badge_fortune">
                    </div>

                    <div class="form-group">
                        <label for="input-date">Simulated Date</label>
                        <input type="date" id="input-date" class="input-control">
                        <button class="btn btn-accent" id="btn-apply-date" style="width: 100%; margin-top: 0.75rem;">⚡ Calculate Daily Seed</button>
                    </div>
                </div>

                <!-- Color Theme configuration -->
                <div class="glass-card sidebar-section">
                    <h2>Color Theme</h2>
                    
                    <div class="switch-container">
                        <span class="switch-label">Auto Theme from Seed</span>
                        <label class="switch">
                            <input type="checkbox" id="switch-auto-theme" checked>
                            <span class="slider"></span>
                        </label>
                    </div>

                    <div class="form-group" id="manual-theme-group" style="opacity: 0.5; pointer-events: none;">
                        <label>Manual Theme Selection</label>
                        <div class="theme-grid">
                            <button class="theme-select-btn" data-theme="0">0</button>
                            <button class="theme-select-btn" data-theme="1">1</button>
                            <button class="theme-select-btn" data-theme="2">2</button>
                            <button class="theme-select-btn" data-theme="3">3</button>
                            <button class="theme-select-btn" data-theme="4">4</button>
                            <button class="theme-select-btn" data-theme="5">5</button>
                        </div>
                    </div>

                    <label style="display: block; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; color: var(--text-secondary); margin-bottom: 0.5rem; font-weight: 600;">Active Theme Colors</label>
                    <div class="color-palette-bar" id="active-theme-colors">
                        <!-- Filled by JS -->
                    </div>
                </div>

            </div>

            <!-- Content Area -->
            <div class="glass-card" style="position: relative; min-height: 500px;">
                <div class="loader-overlay" id="loading-overlay">
                    <div class="spinner"></div>
                    <span>Loading fortunes...</span>
                </div>

                <div class="results-header">
                    <!-- Tab buttons -->
                    <div class="tabs">
                        <button class="tab-btn active" data-tab="paths">Badge Paths (36 Fortunes)</button>
                        <button class="tab-btn" data-tab="sequential">Sequential List (100)</button>
                        <button class="tab-btn" data-tab="dictionary">Manage Dictionary</button>
                        <button class="tab-btn" data-tab="templates">Manage Templates</button>
                    </div>

                    <!-- Filters & Actions -->
                    <div class="toolbar" id="results-toolbar">
                        <div class="search-container">
                            <span class="search-icon">🔍</span>
                            <input type="text" class="search-input" id="search-input" placeholder="Search / filter fortunes...">
                        </div>
                        <button class="btn" id="btn-export" title="Export as Markdown text">📥 Export</button>
                    </div>
                </div>

                <!-- Tab 1: Badge Path Fortunes -->
                <div id="tab-paths" class="tab-content">
                    <div class="colors-grid" id="colors-grid">
                        <!-- Populated by JS -->
                    </div>
                </div>

                <!-- Tab 2: Sequential List -->
                <div id="tab-sequential" class="tab-content hidden">
                    <div class="seq-list" id="seq-list">
                        <!-- Populated by JS -->
                    </div>
                </div>

                <!-- Tab 3: Dictionary Editor -->
                <div id="tab-dictionary" class="tab-content hidden">
                    <div style="margin-bottom: 1.5rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
                        <div style="display: flex; align-items: center; gap: 0.75rem;">
                            <label style="font-weight: 600; text-transform: uppercase; font-size: 0.8rem; color: var(--text-secondary); letter-spacing: 1px;">Category:</label>
                            <select id="dict-category-select" class="input-control" style="width: auto; display: inline-block; padding: 0.4rem 2rem 0.4rem 1rem; font-size: 0.9rem;">
                                <!-- categories populated by JS -->
                            </select>
                        </div>
                        <button class="btn btn-accent" id="btn-save-all-dict">💾 Save All Dictionary Changes</button>
                    </div>
                    <div class="dictionary-view" id="dictionary-view-container">
                        <!-- Filled by JS -->
                    </div>
                </div>

                <!-- Tab 4: Template Editor -->
                <div id="tab-templates" class="tab-content hidden">
                    <div style="margin-bottom: 1.5rem; display: flex; justify-content: space-between; align-items: center;">
                        <h2 style="font-family: var(--font-display); font-size: 1.5rem; font-weight: 600;">Template Manager</h2>
                        <button class="btn btn-accent" id="btn-save-all-templates">💾 Save All Templates Changes</button>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; align-items: start;">
                        <!-- Upbeat Templates Column -->
                        <div class="templates-col glass-card">
                            <h3 style="color: var(--accent-cyan); margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center; font-family: var(--font-display); font-size: 1.15rem;">
                                <span>Upbeat Templates (85% probability)</span>
                                <button class="btn btn-accent" style="padding: 0.35rem 0.6rem; font-size: 0.8rem;" id="btn-add-upbeat-template">+ Add</button>
                            </h3>
                            <div id="upbeat-templates-list" style="display: flex; flex-direction: column; gap: 0.75rem; max-height: 500px; overflow-y: auto; padding-right: 0.25rem;">
                                <!-- Filled by JS -->
                            </div>
                        </div>

                        <!-- Ominous Templates Column -->
                        <div class="templates-col glass-card">
                            <h3 style="color: var(--accent-purple); margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center; font-family: var(--font-display); font-size: 1.15rem;">
                                <span>Ominous Templates (15% probability)</span>
                                <button class="btn btn-accent" style="padding: 0.35rem 0.6rem; font-size: 0.8rem;" id="btn-add-ominous-template">+ Add</button>
                            </h3>
                            <div id="ominous-templates-list" style="display: flex; flex-direction: column; gap: 0.75rem; max-height: 500px; overflow-y: auto; padding-right: 0.25rem;">
                                <!-- Filled by JS -->
                            </div>
                        </div>
                    </div>
                </div>

            </div>

        </div>

        <!-- Footer Info -->
        <footer>
            <p>Tildagon Fortune Teller Simulator • Seeded deterministic choices. Formula matches client micro-python files.</p>
            <p style="margin-top: 0.25rem; opacity: 0.7;">Click any term highlighted in the fortunes above to quickly edit it or view its category options.</p>
        </footer>
    </div>

    <!-- Interactive Term Modal -->
    <div id="term-modal" class="modal-overlay hidden" onclick="closeTermModal()">
        <div class="modal-content glass-card" onclick="event.stopPropagation()">
            <div class="modal-header">
                <h3 id="term-modal-title" style="font-family: var(--font-display);">Edit Term</h3>
                <button class="modal-close" onclick="closeTermModal()">&times;</button>
            </div>
            <div class="modal-body">
                <div class="form-group" style="margin-bottom: 1rem;">
                    <label>Category (Type in Templates)</label>
                    <select id="term-modal-category-select" class="input-control">
                        <!-- Filled by JS -->
                    </select>
                </div>
                
                <div id="term-modal-adj-group" class="form-group" style="display: none; margin-bottom: 1.5rem;">
                    <label>Adjective Variations (for compound term)</label>
                    <div id="term-modal-adj-tabs" style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0.75rem;"></div>
                    <div style="display: flex; gap: 0.5rem; align-items: center;">
                        <span style="font-size: 0.8rem; color: var(--text-secondary);">Selected Tab Adjective:</span>
                        <input type="text" id="term-modal-adj-input" class="input-control" style="flex-grow: 1; padding: 0.4rem 0.6rem;">
                    </div>
                </div>
                
                <div class="form-group">
                    <label>Selected Option</label>
                    <div style="display: flex; gap: 0.5rem; margin-bottom: 0.5rem;">
                        <input type="text" id="term-modal-input" class="input-control" style="flex-grow: 1;">
                        <button class="btn btn-accent" id="term-modal-btn-update">Update</button>
                        <button class="btn" style="background: rgba(255, 70, 70, 0.15); border-color: rgba(255, 70, 70, 0.35); color: rgb(255, 100, 100);" id="term-modal-btn-delete">Remove</button>
                    </div>
                    <div id="term-modal-props-group" style="display: flex; gap: 0.5rem; margin-bottom: 1rem; align-items: center;">
                        <span style="font-size: 0.8rem; color: var(--text-secondary);">Type:</span>
                        <select id="term-modal-type-select" class="input-control" style="width: 120px; padding: 0.4rem 0.6rem;">
                            <option value="countable">Countable</option>
                            <option value="plural">Plural</option>
                            <option value="mass">Mass Noun</option>
                        </select>
                        <span style="font-size: 0.8rem; color: var(--text-secondary);">Unit/Prefix:</span>
                        <input type="text" id="term-modal-unit-input" class="input-control" placeholder="Unit (e.g. bottle of)" style="flex-grow: 1; padding: 0.4rem 0.6rem;">
                    </div>
                </div>

                <div class="form-group">
                    <label>Add New Alternative Option</label>
                    <div style="display: flex; gap: 0.5rem; margin-bottom: 0.5rem;">
                        <input type="text" id="term-modal-add-input" class="input-control" placeholder="Type new term choice..." style="flex-grow: 1;">
                        <button class="btn btn-accent" id="term-modal-btn-add">Add Choice</button>
                    </div>
                    <div id="term-modal-add-props-group" style="display: flex; gap: 0.5rem; margin-bottom: 1.5rem; align-items: center;">
                        <span style="font-size: 0.8rem; color: var(--text-secondary);">Type:</span>
                        <select id="term-modal-add-type-select" class="input-control" style="width: 120px; padding: 0.4rem 0.6rem;">
                            <option value="countable">Countable</option>
                            <option value="plural">Plural</option>
                            <option value="mass">Mass Noun</option>
                        </select>
                        <span style="font-size: 0.8rem; color: var(--text-secondary);">Unit/Prefix:</span>
                        <input type="text" id="term-modal-add-unit-input" class="input-control" placeholder="Unit (e.g. bottle of)" style="flex-grow: 1; padding: 0.4rem 0.6rem;">
                    </div>
                </div>

                <div class="form-group" style="margin-bottom: 0;">
                    <label id="term-modal-options-label">All Available Options in Category</label>
                    <div id="term-modal-options-list" class="modal-options-list">
                        <!-- Filled by JS -->
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Template Previews Modal -->
    <div id="template-previews-modal" class="modal-overlay hidden" onclick="closeTemplatePreviewsModal()">
        <div class="modal-content glass-card" onclick="event.stopPropagation()" style="max-width: 650px;">
            <div class="modal-header">
                <h3 id="template-previews-modal-title" style="font-family: var(--font-display);">Template Previews</h3>
                <button class="modal-close" onclick="closeTemplatePreviewsModal()">&times;</button>
            </div>
            <div class="modal-body">
                <p id="template-previews-modal-template" style="font-family: monospace; padding: 0.5rem; background: rgba(0,0,0,0.3); border-radius: 8px; margin-bottom: 1rem; border: 1px solid var(--panel-border); font-size: 0.95rem; overflow-x: auto; white-space: nowrap;"></p>
                <p style="margin-bottom: 1rem; font-weight: 600; color: var(--accent-cyan);">100 Random Generated Sentences (Based on current seed):</p>
                <div id="template-previews-modal-list" class="modal-options-list" style="max-height: 400px; display: flex; flex-direction: column; gap: 0.5rem; overflow-y: auto;">
                    <!-- Filled by JS -->
                </div>
            </div>
        </div>
    </div>

    <!-- Scripting -->
    <script>
        let currentData = null;
        let activeTab = 'paths';
        let config = {
            MAP_LOCATIONS: [],
            VILLAGES: [],
            TERMS: {},
            UPBEAT_TEMPLATES: [],
            OMINOUS_TEMPLATES: []
        };
        let activeModalKey = '';
        let activeModalRawVal = '';
        let activeModalAdj = '';
        let activeModalSource = '';
        let activeModalItemIdx = -1;
        let activeModalTokenIdx = -1;
        let activeModalVibe = '';
        let activeModalTokens = [];
        let activeModalNoCollective = false;

        // Elements
        const elSeedInput = document.getElementById('input-seed');
        const elBtnRandom = document.getElementById('btn-random-seed');
        const elBtnToday = document.getElementById('btn-today-seed');
        const elBadgeIdInput = document.getElementById('input-badge-id');
        const elDateInput = document.getElementById('input-date');
        const elBtnApplyDate = document.getElementById('btn-apply-date');
        
        const elSwitchAutoTheme = document.getElementById('switch-auto-theme');
        const elManualThemeGroup = document.getElementById('manual-theme-group');
        const elThemeButtons = document.querySelectorAll('.theme-select-btn');
        const elActiveThemeColors = document.getElementById('active-theme-colors');
        
        const elLoadingOverlay = document.getElementById('loading-overlay');
        const elTabButtons = document.querySelectorAll('.tab-btn');
        const elSearchInput = document.getElementById('search-input');
        const elBtnExport = document.getElementById('btn-export');
        const elResultsToolbar = document.getElementById('results-toolbar');
        
        const elColorsGrid = document.getElementById('colors-grid');
        const elSeqList = document.getElementById('seq-list');

        // Modal Elements
        const elTermModal = document.getElementById('term-modal');
        const elTermModalCategorySelect = document.getElementById('term-modal-category-select');
        const elTermModalAdjGroup = document.getElementById('term-modal-adj-group');
        const elTermModalAdjTabs = document.getElementById('term-modal-adj-tabs');
        const elTermModalAdjInput = document.getElementById('term-modal-adj-input');
        const elTermModalInput = document.getElementById('term-modal-input');
        const elTermModalAddInput = document.getElementById('term-modal-add-input');
        const elTermModalOptionsList = document.getElementById('term-modal-options-list');
        const elTermModalBtnUpdate = document.getElementById('term-modal-btn-update');
        const elTermModalBtnDelete = document.getElementById('term-modal-btn-delete');
        const elTermModalBtnAdd = document.getElementById('term-modal-btn-add');
        const elTermModalPropsGroup = document.getElementById('term-modal-props-group');
        const elTermModalTypeSelect = document.getElementById('term-modal-type-select');
        const elTermModalUnitInput = document.getElementById('term-modal-unit-input');
        const elTermModalAddPropsGroup = document.getElementById('term-modal-add-props-group');
        const elTermModalAddTypeSelect = document.getElementById('term-modal-add-type-select');
        const elTermModalAddUnitInput = document.getElementById('term-modal-add-unit-input');

        // Dictionary Elements
        const elDictCategorySelect = document.getElementById('dict-category-select');
        const elDictViewContainer = document.getElementById('dictionary-view-container');
        const elBtnSaveAllDict = document.getElementById('btn-save-all-dict');

        // Template Elements
        const elUpbeatTemplatesList = document.getElementById('upbeat-templates-list');
        const elOminousTemplatesList = document.getElementById('ominous-templates-list');
        const elBtnSaveAllTemplates = document.getElementById('btn-save-all-templates');
        const elBtnAddUpbeatTemplate = document.getElementById('btn-add-upbeat-template');
        const elBtnAddOminousTemplate = document.getElementById('btn-add-ominous-template');

        // Set default date to today
        const todayStr = new Date().toISOString().split('T')[0];
        elDateInput.value = todayStr;

        // Init loads
        document.addEventListener('DOMContentLoaded', () => {
            fetchConfig().then(() => {
                loadFromToday();
                startLiveReload();
            });
        });

        let lastMtime = null;
        function startLiveReload() {
            setInterval(() => {
                fetch('/api/version')
                    .then(res => res.json())
                    .then(data => {
                        if (lastMtime === null) {
                            lastMtime = data.mtime;
                        } else if (data.mtime > lastMtime) {
                            lastMtime = data.mtime;
                            console.log("fortunes.py changed on disk! Live refreshing...");
                            fetchConfig().then(() => {
                                if (activeTab === 'dictionary') {
                                    renderDictionaryTab();
                                } else if (activeTab === 'templates') {
                                    renderTemplatesTab();
                                }
                                const params = { seed: elSeedInput.value };
                                if (!elSwitchAutoTheme.checked) {
                                    const activeThemeBtn = document.querySelector('.theme-select-btn.active');
                                    if (activeThemeBtn) {
                                        params.theme_idx = activeThemeBtn.getAttribute('data-theme');
                                    }
                                }
                                fetchFortunes(params);
                            });
                        }
                    })
                    .catch(err => console.error("Live reload check failed:", err));
            }, 1000);
        }

        // Event Listeners
        elBtnRandom.addEventListener('click', () => {
            const randSeed = Math.floor(Math.random() * 2147483647);
            elSeedInput.value = randSeed;
            fetchFortunes({ seed: randSeed });
        });

        elTermModalCategorySelect.addEventListener('change', () => {
            renderModalOptionsList();
        });

        elTermModalAdjInput.addEventListener('input', () => {
            // Also update the active tab button's text/data if we are currently editing an adjective
            const activeTabBtn = elTermModalAdjTabs.querySelector('.adj-tab-btn.active');
            if (activeTabBtn && !activeTabBtn.classList.contains('adj-tab-btn-add')) {
                const oldAdj = activeTabBtn.getAttribute('data-adj');
                const newAdj = elTermModalAdjInput.value.trim();
                
                const adjKey = (activeModalKey === 'TECH_ITEM') ? 'TECH_ADJECTIVE' : 'CRAFT_ADJECTIVE';
                const adjList = config.TERMS[adjKey];
                if (adjList) {
                    const adjIdx = adjList.indexOf(oldAdj);
                    if (adjIdx !== -1) {
                        adjList[adjIdx] = newAdj;
                    }
                }
                
                activeTabBtn.setAttribute('data-adj', newAdj);
                activeTabBtn.innerText = newAdj || '(blank)';
                // Update the adj variable in memory so preview lists render correctly
                activeModalAdj = newAdj;
                
                updateTotalFortunesCount();
            }
            renderModalOptionsList();
        });

        elTermModalInput.addEventListener('input', () => {
            activeModalRawVal = elTermModalInput.value;
            renderModalOptionsList();
        });

        elTermModalTypeSelect.addEventListener('change', () => {
            renderModalOptionsList();
        });

        elTermModalUnitInput.addEventListener('input', () => {
            renderModalOptionsList();
        });

        elBtnToday.addEventListener('click', () => {
            loadFromToday();
        });

        // Global click listener for color-coded term tokens
        document.addEventListener('click', (e) => {
            const token = e.target.closest('.term-token');
            if (token) {
                const key = token.getAttribute('data-key');
                const rawVal = token.getAttribute('data-raw');
                const source = token.getAttribute('data-source');
                const itemIdx = parseInt(token.getAttribute('data-item-idx'));
                const tokenIdx = parseInt(token.getAttribute('data-token-idx'));
                const template = token.getAttribute('data-template');
                const vibe = token.getAttribute('data-vibe');
                const adj = token.getAttribute('data-adj') || '';
                const noCollective = token.getAttribute('data-no-collective') === 'true';
                
                openTermModal(e, key, rawVal, source, itemIdx, tokenIdx, template, vibe, adj, noCollective);
            }
        });

        elSeedInput.addEventListener('change', () => {
            const queryParams = { seed: elSeedInput.value };
            if (!elSwitchAutoTheme.checked) {
                const activeThemeBtn = document.querySelector('.theme-select-btn.active');
                if (activeThemeBtn) {
                    queryParams.theme_idx = activeThemeBtn.getAttribute('data-theme');
                }
            }
            fetchFortunes(queryParams);
        });

        elBtnApplyDate.addEventListener('click', () => {
            fetchFortunes({
                date: elDateInput.value,
                badge_id: elBadgeIdInput.value
            });
        });

        elSwitchAutoTheme.addEventListener('change', () => {
            if (elSwitchAutoTheme.checked) {
                elManualThemeGroup.style.opacity = '0.5';
                elManualThemeGroup.style.pointerEvents = 'none';
                fetchFortunes({ seed: elSeedInput.value });
            } else {
                elManualThemeGroup.style.opacity = '1';
                elManualThemeGroup.style.pointerEvents = 'auto';
                setThemeButtonActive(0);
                fetchFortunes({
                    seed: elSeedInput.value,
                    theme_idx: 0
                });
            }
        });

        elThemeButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const themeIdx = btn.getAttribute('data-theme');
                setThemeButtonActive(themeIdx);
                fetchFortunes({
                    seed: elSeedInput.value,
                    theme_idx: themeIdx
                });
            });
        });

        elTabButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                elTabButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                const tab = btn.getAttribute('data-tab');
                activeTab = tab;
                
                // Hide all contents
                document.getElementById('tab-paths').classList.add('hidden');
                document.getElementById('tab-sequential').classList.add('hidden');
                document.getElementById('tab-dictionary').classList.add('hidden');
                document.getElementById('tab-templates').classList.add('hidden');
                elResultsToolbar.classList.add('hidden');

                if (tab === 'paths') {
                    document.getElementById('tab-paths').classList.remove('hidden');
                    elResultsToolbar.classList.remove('hidden');
                    filterResults();
                } else if (tab === 'sequential') {
                    document.getElementById('tab-sequential').classList.remove('hidden');
                    elResultsToolbar.classList.remove('hidden');
                    filterResults();
                } else if (tab === 'dictionary') {
                    document.getElementById('tab-dictionary').classList.remove('hidden');
                    renderDictionaryTab();
                } else if (tab === 'templates') {
                    document.getElementById('tab-templates').classList.remove('hidden');
                    renderTemplatesTab();
                }
            });
        });

        elSearchInput.addEventListener('input', () => {
            filterResults();
        });

        elBtnExport.addEventListener('click', () => {
            exportToMarkdown();
        });

        // Config actions
        function fetchConfig() {
            return fetch('/api/config')
                .then(res => res.json())
                .then(data => {
                    config = data;
                    populateCategoryDropdown();
                    updateTotalFortunesCount();
                });
        }

        function saveConfig() {
            elLoadingOverlay.classList.add('active');
            return fetch('/api/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            })
            .then(res => res.json())
            .then(res => {
                if (res.status === 'success') {
                    // Reload config and re-fetch fortunes
                    return fetchConfig().then(() => {
                        const params = { seed: elSeedInput.value };
                        if (!elSwitchAutoTheme.checked) {
                            const activeThemeBtn = document.querySelector('.theme-select-btn.active');
                            if (activeThemeBtn) {
                                params.theme_idx = activeThemeBtn.getAttribute('data-theme');
                            }
                        }
                        return fetchFortunes(params);
                    });
                } else {
                    alert('Error saving configuration: ' + res.message);
                }
            })
            .catch(err => {
                alert('Connection error saving configuration.');
                console.error(err);
            })
            .finally(() => {
                elLoadingOverlay.classList.remove('active');
            });
        }

        // Functions
        function loadFromToday() {
            const today = new Date();
            const y = today.getFullYear();
            const m = String(today.getMonth() + 1).padStart(2, '0');
            const d = String(today.getDate()).padStart(2, '0');
            
            elDateInput.value = `${y}-${m}-${d}`;
            fetchFortunes({
                date: elDateInput.value,
                badge_id: elBadgeIdInput.value
            });
        }

        function setThemeButtonActive(idx) {
            elThemeButtons.forEach(btn => {
                if (btn.getAttribute('data-theme') === String(idx)) {
                    btn.classList.add('active');
                } else {
                    btn.classList.remove('active');
                }
            });
        }

        function fetchFortunes(params = {}) {
            elLoadingOverlay.classList.add('active');
            
            const queryString = Object.keys(params)
                .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
                .join('&');

            fetch(`/api/fortunes?${queryString}`)
                .then(res => res.json())
                .then(data => {
                    currentData = data;
                    
                    // Update outputs
                    elSeedInput.value = data.seed;
                    elBadgeIdInput.value = data.badge_id;
                    elDateInput.value = data.date;

                    // Update theme visual indicators
                    if (data.theme_mode === 'auto') {
                        elSwitchAutoTheme.checked = true;
                        elManualThemeGroup.style.opacity = '0.5';
                        elManualThemeGroup.style.pointerEvents = 'none';
                        setThemeButtonActive(data.theme_idx);
                    } else {
                        elSwitchAutoTheme.checked = false;
                        elManualThemeGroup.style.opacity = '1';
                        elManualThemeGroup.style.pointerEvents = 'auto';
                        setThemeButtonActive(data.theme_idx);
                    }

                    // Dynamically set CSS variables for theme colors
                    data.theme_colors.forEach((col, idx) => {
                        const rgbStr = `${col.rgb[0]}, ${col.rgb[1]}, ${col.rgb[2]}`;
                        document.documentElement.style.setProperty(`--theme-color-${idx}`, `rgb(${rgbStr})`);
                        document.documentElement.style.setProperty(`--theme-color-${idx}-alpha`, `rgba(${rgbStr}, 0.08)`);
                        document.documentElement.style.setProperty(`--theme-color-${idx}-border`, `rgba(${rgbStr}, 0.25)`);
                    });

                    renderThemePalette(data.theme_colors);
                    renderBadgePaths(data.paths);
                    renderSequential(data.sequential);
                    filterResults();
                    
                    elLoadingOverlay.classList.remove('active');
                })
                .catch(err => {
                    console.error("Error fetching fortunes: ", err);
                    elLoadingOverlay.classList.remove('active');
                    alert("Error loading fortunes from server.");
                });
        }

        function renderThemePalette(colors) {
            elActiveThemeColors.innerHTML = '';
            colors.forEach((col, idx) => {
                const rgb = `rgb(${col.rgb[0]},${col.rgb[1]},${col.rgb[2]})`;
                
                const dot = document.createElement('div');
                dot.className = 'color-dot';
                dot.style.backgroundColor = rgb;
                dot.style.color = '#fff';
                dot.innerText = col.name;
                elActiveThemeColors.appendChild(dot);
            });
        }

        // Color coding tokens formatter
        function formatTokens(tokens, source, itemIdx, template, vibe) {
            return tokens.map((t, tokenIdx) => {
                if (t.type === 'text') {
                    return escapeHtml(t.value);
                } else {
                    const adjAttr = t.adj ? ` data-adj="${escapeHtml(t.adj)}"` : '';
                    const noCollAttr = t.no_collective ? ` data-no-collective="true"` : '';
                    return `<span class="term-token term-key-${t.key}" data-key="${t.key}" data-raw="${escapeHtml(t.raw_value)}"${adjAttr}${noCollAttr} data-source="${source}" data-item-idx="${itemIdx}" data-token-idx="${tokenIdx}" data-template="${escapeHtml(template)}" data-vibe="${vibe}">${escapeHtml(t.value)}</span>`;
                }
            }).join('');
        }

        function escapeHtml(unsafe) {
            return unsafe
                 .replace(/&/g, "&amp;")
                 .replace(/</g, "&lt;")
                 .replace(/>/g, "&gt;")
                 .replace(/"/g, "&quot;")
                 .replace(/'/g, "&#039;");
        }

        function renderBadgePaths(paths) {
            elColorsGrid.innerHTML = '';
            
            // Group by color index
            const groups = {};
            paths.forEach((p, globalIdx) => {
                p._globalIdx = globalIdx;
                if (!groups[p.color_idx]) {
                    groups[p.color_idx] = [];
                }
                groups[p.color_idx].push(p);
            });

            // For each of the 6 colors
            for (let i = 0; i < 6; i++) {
                const colorPaths = groups[i];
                if (!colorPaths) continue;

                const firstPath = colorPaths[0];
                const rgbStr = `var(--theme-color-${i})`;
                const borderStr = `var(--theme-color-${i}-border)`;
                const bgAlphaStr = `var(--theme-color-${i}-alpha)`;

                const card = document.createElement('div');
                card.className = 'color-card';
                card.style.setProperty('--border-color', borderStr);
                card.style.setProperty('--bg-alpha', bgAlphaStr);
                
                const header = document.createElement('div');
                header.className = 'color-card-header';
                header.style.color = rgbStr;
                header.innerHTML = `
                    <span>Corner ${i + 1} (${getCornerLabel(i + 1)})</span>
                    <span class="color-pill" style="background-color: rgba(255,255,255,0.06); color: ${rgbStr}; border-color: ${borderStr};">${firstPath.color_name}</span>
                `;
                card.appendChild(header);

                const list = document.createElement('div');
                list.className = 'fortunes-list';

                colorPaths.forEach((p) => {
                    const item = document.createElement('div');
                    item.className = 'fortune-item';
                    item.style.setProperty('--btn-color', rgbStr);
                    
                    item.innerHTML = `
                        <div class="fortune-number">${p.number}</div>
                        <div class="fortune-text-box">
                            <span class="fortune-text">${formatTokens(p.tokens, 'paths', p._globalIdx, p.template, p.vibe)}</span>
                            <span class="fortune-meta">seed: ${p.path_seed} &bull; template: <span class="edit-template-link" onclick="navigateToTemplate(event, '${escapeHtml(p.template)}', '${p.vibe}')" style="font-family: monospace; color: var(--accent-cyan); text-decoration: underline; cursor: pointer; opacity: 0.85;">${escapeHtml(p.template)}</span></span>
                        </div>
                    `;
                    list.appendChild(item);
                });

                card.appendChild(list);
                elColorsGrid.appendChild(card);
            }
        }

        function renderSequential(sequential) {
            elSeqList.innerHTML = '';
            sequential.forEach((s, sIdx) => {
                const item = document.createElement('div');
                item.className = 'seq-item';
                item.innerHTML = `
                    <div class="seq-badge">#${s.index}</div>
                    <div class="seq-content">
                        <div class="fortune-text">${formatTokens(s.tokens, 'sequential', sIdx, s.template, s.vibe)}</div>
                        <div class="seq-seed">Seed: ${s.seed} &bull; template: <span class="edit-template-link" onclick="navigateToTemplate(event, '${escapeHtml(s.template)}', '${s.vibe}')" style="font-family: monospace; color: var(--accent-cyan); text-decoration: underline; cursor: pointer; opacity: 0.85;">${escapeHtml(s.template)}</span></div>
                    </div>
                `;
                elSeqList.appendChild(item);
            });
        }

        window.navigateToTemplate = function(e, templateText, vibe) {
            if (e) e.preventDefault();
            
            // Switch tab to 'templates'
            const tabBtn = document.querySelector('.tab-btn[data-tab="templates"]');
            if (tabBtn) tabBtn.click();
            
            // Find template and its index
            const tplList = (vibe === 'upbeat') ? config.UPBEAT_TEMPLATES : config.OMINOUS_TEMPLATES;
            const idx = tplList.indexOf(templateText);
            if (idx === -1) return;
            
            // Wait for DOM to render list items
            setTimeout(() => {
                const targetId = `template-item-${vibe}-${idx}`;
                const targetEl = document.getElementById(targetId);
                if (targetEl) {
                    targetEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    
                    const textarea = targetEl.querySelector('.template-textarea');
                    if (textarea) {
                        textarea.focus();
                        textarea.style.boxShadow = '0 0 15px var(--accent-cyan)';
                        textarea.style.borderColor = 'var(--accent-cyan)';
                        setTimeout(() => {
                            textarea.style.boxShadow = '';
                            textarea.style.borderColor = '';
                        }, 2000);
                    }
                }
            }, 150);
        };

        class SeededRandomJS {
            constructor(seedVal) {
                this.state = seedVal & 0xFFFFFFFF;
                if (this.state === 0) {
                    this.state = 123456789;
                }
            }
            nextInt() {
                this.state = (Math.imul(this.state, 1103515245) + 12345) & 0x7FFFFFFF;
                return this.state;
            }
            choice(lst) {
                if (!lst || lst.length === 0) return null;
                return lst[this.nextInt() % lst.length];
            }
        }

        function chooseUniqueJS(rng, values, usedTerms) {
            const available = values.filter(v => {
                const raw = Array.isArray(v) ? v[0] : v;
                return !usedTerms.has(raw);
            });
            const listToUse = available.length > 0 ? available : values;
            const choice = rng.choice(listToUse);
            const raw = Array.isArray(choice) ? choice[0] : choice;
            usedTerms.add(raw);
            return choice;
        }

        function generateFortuneJS(template, stepSeed) {
            let rng = new SeededRandomJS(stepSeed);
            let result = template;
            let usedTerms = new Set();

            // Resolve compound placeholders first
            while (result.includes("{TECH_ADJECTIVE_ITEM}")) {
                const adj = chooseUniqueJS(rng, config.TERMS["TECH_ADJECTIVE"], usedTerms);
                const item = chooseUniqueJS(rng, config.TERMS["TECH_ITEM"], usedTerms);
                const val = formatItemJS(adj, item, rng);
                result = result.replace("{TECH_ADJECTIVE_ITEM}", val);
            }

            while (result.includes("{CRAFT_ADJECTIVE_ITEM}")) {
                const adj = chooseUniqueJS(rng, config.TERMS["CRAFT_ADJECTIVE"], usedTerms);
                const item = chooseUniqueJS(rng, config.TERMS["CRAFT_ITEM"], usedTerms);
                const val = formatItemJS(adj, item, rng);
                result = result.replace("{CRAFT_ADJECTIVE_ITEM}", val);
            }

            while (result.includes("{TECH_SHINY_ITEM}")) {
                const item = chooseUniqueJS(rng, config.TERMS["TECH_ITEM"], usedTerms);
                const val = formatItemJS("shiny", item, rng);
                result = result.replace("{TECH_SHINY_ITEM}", val);
            }

            while (result.includes("{TECH_RARE_ITEM}")) {
                const item = chooseUniqueJS(rng, config.TERMS["TECH_ITEM"], usedTerms);
                const val = formatItemJS("rare", item, rng);
                result = result.replace("{TECH_RARE_ITEM}", val);
            }

            const keys = ['MAP_LOCATION', 'VILLAGE', 'DESTINATION', ...Object.keys(config.TERMS).filter(k => k !== 'MAP_LOCATION' && k !== 'VILLAGE' && k !== 'DESTINATION')];
            
            keys.forEach(key => {
                let placeholders = [];
                if (key === 'CREATURE_PLURAL') {
                    placeholders = [
                        { name: '{CREATURE_PLURAL}', noColl: true },
                        { name: '{CREATURE_PLURAL_COLLECTIVE}', noColl: false }
                    ];
                } else if (key === 'PEOPLE_SUBJECT') {
                    placeholders = [
                        { name: '{PEOPLE_SUBJECT}', noColl: true },
                        { name: '{PEOPLE_SUBJECT_COLLECTIVE}', noColl: false }
                    ];
                } else {
                    placeholders = [
                        { name: '{' + key + '}', noColl: false }
                    ];
                }

                const values = getOptionsListForKey(key);
                if (!values || values.length === 0) return;
                
                placeholders.forEach(p => {
                    while (result.includes(p.name)) {
                        const choice = chooseUniqueJS(rng, values, usedTerms);
                        let displayVal = choice;
                        if (key === 'VILLAGE' || (key === 'DESTINATION' && config.VILLAGES.includes(choice))) {
                            displayVal = formatVillageJS(choice);
                        } else if (Array.isArray(choice)) {
                            displayVal = formatItemJS("", choice, rng, p.noColl);
                        }
                        result = result.replace(p.name, displayVal);
                    }
                });
            });
            
            if (result) {
                result = result.charAt(0).toUpperCase() + result.slice(1);
                result = fixAAnJS(result);
            }
            return result;
        }

        window.openTemplatePreviewsModal = function(template) {
            const elModal = document.getElementById('template-previews-modal');
            const elTpl = document.getElementById('template-previews-modal-template');
            const elList = document.getElementById('template-previews-modal-list');
            
            elTpl.innerText = template;
            elList.innerHTML = '';
            
            const baseSeed = parseInt(elSeedInput.value) || 0;
            const seqRng = new SeededRandomJS(baseSeed);
            
            const uniqueFortunes = new Set();
            let attempts = 0;
            // Generate up to 100 unique variations, but cap attempts to 1000 to prevent infinite loops
            while (uniqueFortunes.size < 100 && attempts < 1000) {
                const stepSeed = seqRng.nextInt();
                const fortune = generateFortuneJS(template, stepSeed);
                uniqueFortunes.add(fortune);
                attempts++;
            }
            
            let i = 0;
            uniqueFortunes.forEach(fortune => {
                const item = document.createElement('div');
                item.className = 'modal-option-item';
                item.style.cursor = 'default';
                item.innerText = `#${i + 1}: ${fortune}`;
                elList.appendChild(item);
                i++;
            });
            
            elModal.classList.remove('hidden');
        };

        window.closeTemplatePreviewsModal = function() {
            document.getElementById('template-previews-modal').classList.add('hidden');
        };

        function getCornerLabel(num) {
            const labels = {
                1: 'UP',
                2: 'RIGHT',
                3: 'CONFIRM',
                4: 'DOWN',
                5: 'LEFT',
                6: 'CANCEL'
            };
            return labels[num] || '';
        }

        function filterResults() {
            const query = elSearchInput.value.toLowerCase().trim();
            
            if (activeTab === 'paths') {
                const cards = elColorsGrid.querySelectorAll('.color-card');
                
                cards.forEach(card => {
                    let hasVisibleItem = false;
                    const cItems = card.querySelectorAll('.fortune-item');
                    
                    cItems.forEach(item => {
                        const txtBox = item.querySelector('.fortune-text');
                        const origText = txtBox ? txtBox.textContent.toLowerCase() : '';
                        const metaBox = item.querySelector('.fortune-meta');
                        const metaText = metaBox ? metaBox.textContent.toLowerCase() : '';
                        
                        if (!query) {
                            item.classList.remove('hidden');
                            hasVisibleItem = true;
                        } else if (origText.includes(query) || metaText.includes(query)) {
                            item.classList.remove('hidden');
                            hasVisibleItem = true;
                        } else {
                            item.classList.add('hidden');
                        }
                    });

                    if (hasVisibleItem) {
                        card.classList.remove('hidden');
                    } else {
                        card.classList.add('hidden');
                    }
                });
            } else if (activeTab === 'sequential') {
                const items = elSeqList.querySelectorAll('.seq-item');
                items.forEach(item => {
                    const txtBox = item.querySelector('.fortune-text');
                    const origText = txtBox ? txtBox.textContent.toLowerCase() : '';
                    const seedBox = item.querySelector('.seq-seed');
                    const seedText = seedBox ? seedBox.textContent.toLowerCase() : '';
                    
                    if (!query) {
                        item.classList.remove('hidden');
                    } else if (origText.includes(query) || seedText.includes(query)) {
                        item.classList.remove('hidden');
                    } else {
                        item.classList.add('hidden');
                    }
                });
            }
        }

        function exportToMarkdown() {
            if (!currentData) return;

            let md = `# Tildagon Fortune Teller Review Report\n\n`;
            md += `* **Generated on:** ${new Date().toLocaleString()}\n`;
            md += `* **Base Seed:** ${currentData.seed}\n`;
            md += `* **Theme Index:** ${currentData.theme_idx} (${currentData.theme_mode === 'auto' ? 'Calculated' : 'Manual Overridden'})\n`;
            md += `* **Date Context:** ${currentData.date}\n`;
            md += `* **Badge ID:** ${currentData.badge_id}\n\n`;
            
            md += `## 36 Path Fortunes (By Badge Colors/Buttons)\n\n`;
            
            const groups = {};
            currentData.paths.forEach(p => {
                if (!groups[p.color_idx]) groups[p.color_idx] = [];
                groups[p.color_idx].push(p);
            });

            for (let i = 0; i < 6; i++) {
                const colPaths = groups[i];
                if (!colPaths) continue;
                md += `### Corner ${i + 1} - ${colPaths[0].color_name} (${getCornerLabel(i + 1)})\n\n`;
                colPaths.forEach(p => {
                    md += `* **Number ${p.number}:** ${p.fortune} *(path seed: ${p.path_seed})*\n`;
                });
                md += `\n`;
            }

            md += `## First 20 Sequential Outcomes\n\n`;
            for (let i = 0; i < 20; i++) {
                const s = currentData.sequential[i];
                md += `${s.index}. ${s.fortune} *(seed: ${s.seed})*\n`;
            }

            navigator.clipboard.writeText(md).then(() => {
                alert("Copied Review Report in Markdown format to clipboard!");
            }).catch(err => {
                console.error("Clipboard copy failed: ", err);
                const blob = new Blob([md], {type: 'text/markdown'});
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `fortune_teller_review_${currentData.seed}.md`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            });
        }

        function replaceNthPlaceholder(template, n, newPlaceholder) {
            const regex = /\{([A-Z_]+)\}/g;
            let count = 0;
            return template.replace(regex, (match) => {
                if (count === n) {
                    count++;
                    return `{${newPlaceholder}}`;
                }
                count++;
                return match;
            });
        }

        // Modal interactive actions
        window.openTermModal = function(e, key, rawVal, source, itemIdx, tokenIdx, template, vibe, adj = '', noCollective = false) {
            e.stopPropagation();
            activeModalKey = key;
            activeModalRawVal = rawVal;
            activeModalAdj = adj;
            activeModalSource = source;
            activeModalItemIdx = itemIdx;
            activeModalTokenIdx = tokenIdx;
            activeModalTemplate = template;
            activeModalVibe = vibe;
            activeModalNoCollective = noCollective;

            if (source === 'paths') {
                activeModalTokens = currentData.paths[itemIdx].tokens;
            } else {
                activeModalTokens = currentData.sequential[itemIdx].tokens;
            }

            // Populate category select options
            elTermModalCategorySelect.innerHTML = '';
            
            const categories = [
                { key: 'MAP_LOCATION', label: 'MAP_LOCATION' },
                { key: 'VILLAGE', label: 'VILLAGE' },
                { key: 'DESTINATION', label: 'DESTINATION' },
                ...Object.keys(config.TERMS).filter(k => k !== 'DESTINATION' && k !== 'MAP_LOCATION' && k !== 'VILLAGE').map(k => ({ key: k, label: k }))
            ];
            
            categories.forEach(cat => {
                const opt = document.createElement('option');
                opt.value = cat.key;
                opt.innerText = cat.label;
                elTermModalCategorySelect.appendChild(opt);
            });
            
            elTermModalCategorySelect.value = key;
            elTermModalInput.value = rawVal;
            elTermModalAddInput.value = '';

            // Handle Adjective compound input visibility
            if (adj) {
                elTermModalAdjGroup.style.display = 'block';
                
                const adjKey = (key === 'TECH_ITEM') ? 'TECH_ADJECTIVE' : 'CRAFT_ADJECTIVE';
                let adjList = config.TERMS[adjKey] ? [...config.TERMS[adjKey]] : [];
                if (adjList.length === 0 && (adj === 'shiny' || adj === 'rare')) {
                    adjList = [adj];
                } else if (adj && !adjList.includes(adj)) {
                    adjList.push(adj);
                }
                
                const drawTabs = (selectedAdj) => {
                    elTermModalAdjTabs.innerHTML = '';
                    adjList.forEach((a, index) => {
                        const tabBtn = document.createElement('button');
                        tabBtn.className = 'adj-tab-btn' + (a === selectedAdj ? ' active' : '');
                        tabBtn.innerText = a || '(blank)';
                        tabBtn.setAttribute('data-adj', a);
                        tabBtn.setAttribute('data-idx', index);
                        tabBtn.addEventListener('click', (ev) => {
                            ev.preventDefault();
                            elTermModalAdjTabs.querySelectorAll('.adj-tab-btn').forEach(btn => btn.classList.remove('active'));
                            tabBtn.classList.add('active');
                            elTermModalAdjInput.value = a;
                            activeModalAdj = a;
                            renderModalOptionsList();
                        });
                        elTermModalAdjTabs.appendChild(tabBtn);
                    });
                    
                    const addTabBtn = document.createElement('button');
                    addTabBtn.className = 'adj-tab-btn adj-tab-btn-add';
                    addTabBtn.innerText = '+ New';
                    addTabBtn.addEventListener('click', (ev) => {
                        ev.preventDefault();
                        const newAdj = prompt("Enter new adjective variation:");
                        if (newAdj && newAdj.trim()) {
                            const trimmed = newAdj.trim();
                            if (!adjList.includes(trimmed)) {
                                adjList.push(trimmed);
                                if (config.TERMS[adjKey] && !config.TERMS[adjKey].includes(trimmed)) {
                                    config.TERMS[adjKey].push(trimmed);
                                }
                            }
                            drawTabs(trimmed);
                            elTermModalAdjInput.value = trimmed;
                            activeModalAdj = trimmed;
                            renderModalOptionsList();
                            updateTotalFortunesCount();
                        }
                    });
                    elTermModalAdjTabs.appendChild(addTabBtn);
                };
                
                drawTabs(adj);
                elTermModalAdjInput.value = adj;
            } else {
                elTermModalAdjGroup.style.display = 'none';
                elTermModalAdjInput.value = '';
                elTermModalAdjTabs.innerHTML = '';
            }

            // Handle type and unit props input visibility
            const showProps = (key !== 'MAP_LOCATION' && key !== 'VILLAGE' && key !== 'DESTINATION');
            if (showProps) {
                elTermModalPropsGroup.style.display = 'flex';
                elTermModalAddPropsGroup.style.display = 'flex';
                
                const targetList = getTargetStateList(key);
                const foundItem = targetList.find(item => (Array.isArray(item) ? item[0] : item) === rawVal);
                if (Array.isArray(foundItem)) {
                    elTermModalTypeSelect.value = foundItem[1] || 'countable';
                    elTermModalUnitInput.value = foundItem[2] || '';
                } else {
                    elTermModalTypeSelect.value = 'countable';
                    elTermModalUnitInput.value = '';
                }
            } else {
                elTermModalPropsGroup.style.display = 'none';
                elTermModalAddPropsGroup.style.display = 'none';
            }

            renderModalOptionsList();
            elTermModal.classList.remove('hidden');
        };

        window.closeTermModal = function() {
            elTermModal.classList.add('hidden');
        };

        function getOptionsListForKey(key) {
            if (key === 'MAP_LOCATION') return config.MAP_LOCATIONS;
            if (key === 'VILLAGE') return config.VILLAGES;
            if (key === 'DESTINATION') return [...config.MAP_LOCATIONS, ...config.VILLAGES];
            return config.TERMS[key] || [];
        }

        const COLLECTIVE_PREFIXES_JS = [
            "herd of",
            "gaggle of",
            "conference of",
            "swarm of",
            "parade of",
            "tsunami of",
            "mob of",
            "cabal of",
            "flock of"
        ];

        function formatItemJS(adjective, item, rng, noCollective = false) {
            let name, itype, unit;
            if (Array.isArray(item)) {
                name = item[0];
                itype = item[1];
                unit = item.length > 2 ? item[2] : null;
            } else {
                name = item;
                itype = "countable";
                unit = null;
            }

            if (itype === "plural" && !unit && !noCollective) {
                if (rng) {
                    if (rng.nextInt() % 2 === 0) {
                        unit = rng.choice(COLLECTIVE_PREFIXES_JS);
                    }
                } else {
                    unit = "gaggle of";
                }
            }

            if (unit) {
                let phrase = adjective ? `${unit} ${adjective} ${name}` : `${unit} ${name}`;
                return fixAAnJS(`a ${phrase}`);
            } else {
                let phrase = adjective ? `${adjective} ${name}` : `${name}`;
                if (itype === "countable") {
                    return fixAAnJS(`a ${phrase}`);
                }
                return phrase;
            }
        }

        function fixAAnTokensJS(tokens) {
            let vowels = "aeiouAEIOU";
            function getNextWord(startIdx) {
                for (let j = startIdx; j < tokens.length; j++) {
                    let val = tokens[j].value;
                    let words = val.trim().split(/\s+/);
                    if (words.length > 0 && words[0]) {
                        return words[0].replace(/^[`"'(]+/, "");
                    }
                }
                return "";
            }
            for (let i = 0; i < tokens.length; i++) {
                let token = tokens[i];
                if (token.type === 'text') {
                    let val = token.value;
                    let parts = val.split(" ");
                    let changed = false;
                    for (let p_idx = 0; p_idx < parts.length; p_idx++) {
                        let word = parts[p_idx];
                        if (word === "a" || (word === "A" && i === 0 && p_idx === 0)) {
                            let next_w = "";
                            if (p_idx + 1 < parts.length) {
                                  for (let k = p_idx + 1; k < parts.length; k++) {
                                      if (parts[k]) {
                                          next_w = parts[k].replace(/^[`"'(]+/, "");
                                          break;
                                      }
                                  }
                            }
                            if (!next_w) {
                                next_w = getNextWord(i + 1);
                            }
                            if (next_w && vowels.includes(next_w[0])) {
                                parts[p_idx] = (word === "A") ? "An" : "an";
                                changed = true;
                            }
                        }
                    }
                    if (changed) {
                        token.value = parts.join(" ");
                    }
                }
            }
        }

        function renderModalOptionsList() {
            elTermModalOptionsList.innerHTML = '';
            const selectedCategory = elTermModalCategorySelect.value;
            const opts = getOptionsListForKey(selectedCategory);
            
            opts.forEach(opt => {
                const optName = Array.isArray(opt) ? opt[0] : opt;
                const elOpt = document.createElement('div');
                elOpt.className = 'modal-option-item';
                if (optName === activeModalRawVal && selectedCategory === activeModalKey) {
                    elOpt.classList.add('active');
                }
                
                // Construct the preview sentence tokens
                const currentAdj = elTermModalAdjGroup.style.display !== 'none' ? elTermModalAdjInput.value : '';
                const previewTokens = activeModalTokens.map((t, idx) => {
                    if (idx === activeModalTokenIdx) {
                        let displayVal = optName;
                        if (selectedCategory === 'VILLAGE' || (selectedCategory === 'DESTINATION' && config.VILLAGES.includes(optName))) {
                            displayVal = formatVillageJS(optName);
                        } else if (selectedCategory !== 'MAP_LOCATION' && selectedCategory !== 'VILLAGE' && selectedCategory !== 'DESTINATION') {
                            let itemToFormat = opt;
                            if (optName === activeModalRawVal) {
                                const nameVal = elTermModalInput.value.trim() || optName;
                                const typeVal = elTermModalTypeSelect.value;
                                const unitVal = elTermModalUnitInput.value.trim();
                                itemToFormat = unitVal ? [nameVal, typeVal, unitVal] : [nameVal, typeVal];
                            }
                            displayVal = formatItemJS(currentAdj, itemToFormat, null, (selectedCategory === 'CREATURE_PLURAL' || selectedCategory === 'PEOPLE_SUBJECT') && activeModalNoCollective);
                        }
                        return { type: 'term', value: displayVal };
                    }
                    return { type: t.type, value: t.value };
                });
                
                // Capitalize first token
                if (previewTokens.length > 0) {
                    let firstVal = previewTokens[0].value;
                    previewTokens[0].value = firstVal.charAt(0).toUpperCase() + firstVal.slice(1);
                }
                
                // Fix a/an on tokens
                fixAAnTokensJS(previewTokens);
                
                // Construct final HTML with term highlight
                const previewHtml = previewTokens.map((t, idx) => {
                    if (idx === activeModalTokenIdx) {
                        return `<span class="term-token term-key-${selectedCategory}" style="font-weight: 600; border-bottom: 2px solid var(--accent-cyan); padding: 0 2px;">${escapeHtml(t.value)}</span>`;
                    }
                    return escapeHtml(t.value);
                }).join('');
                
                elOpt.innerHTML = previewHtml;
                
                elOpt.addEventListener('click', () => {
                    elTermModalInput.value = optName;
                    activeModalRawVal = optName;
                    elTermModalOptionsList.querySelectorAll('.modal-option-item').forEach(x => x.classList.remove('active'));
                    elOpt.classList.add('active');
                });
                
                elTermModalOptionsList.appendChild(elOpt);
            });
        }

        elTermModalBtnUpdate.addEventListener('click', () => {
            const newVal = elTermModalInput.value.trim();
            if (!newVal) return;

            const newCategory = elTermModalCategorySelect.value;
            const showProps = (newCategory !== 'MAP_LOCATION' && newCategory !== 'VILLAGE' && newCategory !== 'DESTINATION');

            // Handle adjective update for compound terms
            if (activeModalAdj) {
                const newAdj = elTermModalAdjInput.value.trim();
                if (newAdj && newAdj !== activeModalAdj) {
                    const adjKey = (activeModalKey === 'TECH_ITEM') ? 'TECH_ADJECTIVE' : 'CRAFT_ADJECTIVE';
                    const adjList = config.TERMS[adjKey];
                    if (adjList) {
                        const adjIdx = adjList.indexOf(activeModalAdj);
                        if (adjIdx !== -1) {
                            adjList[adjIdx] = newAdj;
                        }
                    }
                }
            }

            // Find template and update placeholder tag if category changed
            if (newCategory !== activeModalKey) {
                let termOccurrenceIdx = 0;
                for (let i = 0; i < activeModalTokenIdx; i++) {
                    if (activeModalTokens[i].type === 'term') {
                        termOccurrenceIdx++;
                    }
                }
                let tplList = (activeModalVibe === 'upbeat') ? config.UPBEAT_TEMPLATES : config.OMINOUS_TEMPLATES;
                let tplIdx = tplList.indexOf(activeModalTemplate);
                if (tplIdx !== -1) {
                    tplList[tplIdx] = replaceNthPlaceholder(activeModalTemplate, termOccurrenceIdx, newCategory);
                }
                
                // Add the custom value to the new category list if it's new
                const newList = getTargetStateList(newCategory);
                if (newList) {
                    const exists = newList.some(item => (Array.isArray(item) ? item[0] : item) === newVal);
                    if (!exists) {
                        if (showProps) {
                            const newType = elTermModalTypeSelect.value;
                            const newUnit = elTermModalUnitInput.value.trim();
                            if (newUnit) {
                                newList.push([newVal, newType, newUnit]);
                            } else {
                                newList.push([newVal, newType]);
                            }
                        } else {
                            newList.push(newVal);
                        }
                    }
                }
            } else {
                // Same category, update the value in dictionary or add it
                const targetList = getTargetStateList(activeModalKey);
                if (targetList) {
                    const idx = targetList.findIndex(item => (Array.isArray(item) ? item[0] : item) === activeModalRawVal);
                    if (idx !== -1) {
                        if (showProps) {
                            const newType = elTermModalTypeSelect.value;
                            const newUnit = elTermModalUnitInput.value.trim();
                            if (newUnit) {
                                targetList[idx] = [newVal, newType, newUnit];
                            } else {
                                targetList[idx] = [newVal, newType];
                            }
                        } else {
                            targetList[idx] = newVal;
                        }
                    } else {
                        const exists = targetList.some(item => (Array.isArray(item) ? item[0] : item) === newVal);
                        if (!exists) {
                            if (showProps) {
                                const newType = elTermModalTypeSelect.value;
                                const newUnit = elTermModalUnitInput.value.trim();
                                if (newUnit) {
                                    targetList.push([newVal, newType, newUnit]);
                                } else {
                                    targetList.push([newVal, newType]);
                                }
                            } else {
                                targetList.push(newVal);
                            }
                        }
                    }
                }
            }
            saveConfig().then(() => closeTermModal());
        });

        elTermModalBtnDelete.addEventListener('click', () => {
            const targetList = getTargetStateList(activeModalKey);
            if (!targetList) return;

            const idx = targetList.findIndex(item => (Array.isArray(item) ? item[0] : item) === activeModalRawVal);
            if (idx !== -1) {
                targetList.splice(idx, 1);
                saveConfig().then(() => closeTermModal());
            }
        });

        elTermModalBtnAdd.addEventListener('click', () => {
            const addVal = elTermModalAddInput.value.trim();
            if (!addVal) return;

            const targetList = getTargetStateList(activeModalKey);
            if (!targetList) return;

            const exists = targetList.some(item => (Array.isArray(item) ? item[0] : item) === addVal);
            if (!exists) {
                const showProps = (activeModalKey !== 'MAP_LOCATION' && activeModalKey !== 'VILLAGE' && activeModalKey !== 'DESTINATION');
                if (showProps) {
                    const addType = elTermModalAddTypeSelect.value;
                    const addUnit = elTermModalAddUnitInput.value.trim();
                    if (addUnit) {
                        targetList.push([addVal, addType, addUnit]);
                    } else {
                        targetList.push([addVal, addType]);
                    }
                } else {
                    targetList.push(addVal);
                }
                saveConfig().then(() => {
                    elTermModalAddInput.value = '';
                    elTermModalAddUnitInput.value = '';
                    renderModalOptionsList();
                });
            }
        });

        function getTargetStateList(key) {
            if (key === 'MAP_LOCATION') return config.MAP_LOCATIONS;
            if (key === 'VILLAGE') return config.VILLAGES;
            if (key === 'DESTINATION') {
                // If it is DESTINATION, we have to decide where it belongs:
                // typically destination is MAP_LOCATIONS or VILLAGES. Let's find where it exists, or append to VILLAGES as default.
                if (config.MAP_LOCATIONS.includes(activeModalRawVal)) return config.MAP_LOCATIONS;
                return config.VILLAGES;
            }
            return config.TERMS[key];
        }

        // Dictionary tab functions
        function populateCategoryDropdown() {
            elDictCategorySelect.innerHTML = '';
            
            const categories = [
                { key: 'MAP_LOCATIONS', label: 'MAP LOCATIONS (campsite areas)' },
                { key: 'VILLAGES', label: 'VILLAGES (EMF villages list)' },
                ...Object.keys(config.TERMS).map(k => ({ key: k, label: k }))
            ];

            categories.forEach(cat => {
                const opt = document.createElement('option');
                opt.value = cat.key;
                opt.innerText = cat.label;
                elDictCategorySelect.appendChild(opt);
            });

            elDictCategorySelect.addEventListener('change', () => {
                renderCategoryTerms(elDictCategorySelect.value);
            });
        }

        function renderDictionaryTab() {
            if (elDictCategorySelect.value) {
                renderCategoryTerms(elDictCategorySelect.value);
            } else if (elDictCategorySelect.firstElementChild) {
                renderCategoryTerms(elDictCategorySelect.firstElementChild.value);
            }
        }

        function getListFromConfigKey(key) {
            if (key === 'MAP_LOCATIONS') return config.MAP_LOCATIONS;
            if (key === 'VILLAGES') return config.VILLAGES;
            return config.TERMS[key];
        }

        function renderCategoryTerms(key) {
            elDictViewContainer.innerHTML = '';
            const list = getListFromConfigKey(key);
            if (!list) return;

            const card = document.createElement('div');
            card.className = 'dict-category-card';

            const title = document.createElement('div');
            title.className = 'dict-category-title';
            title.innerHTML = `
                <span>Category Options Count: ${list.length}</span>
                <div style="display: flex; gap: 0.5rem;">
                    <input type="text" id="dict-bulk-add-input" class="input-control" placeholder="Add new item to list..." style="padding: 0.4rem 0.8rem; font-size: 0.85rem; width: 220px;">
                    <button class="btn btn-accent" style="padding: 0.4rem 0.8rem; font-size: 0.85rem;" id="btn-dict-bulk-add">Add Choice</button>
                </div>
            `;
            card.appendChild(title);

            const grid = document.createElement('div');
            grid.className = 'dict-terms-grid';

            list.forEach((term, idx) => {
                const isArr = Array.isArray(term);
                const termName = isArr ? term[0] : term;
                const row = document.createElement('div');
                row.className = 'dict-term-editable';
                
                if (isArr) {
                    const type = term[1] || 'countable';
                    const unit = term[2] || '';
                    row.innerHTML = `
                        <span style="font-size: 0.85rem; color: var(--text-secondary); font-weight: 600; white-space: nowrap;">Term:</span>
                        <input type="text" class="dict-term-input input-control" value="${escapeHtml(termName)}" style="flex-grow: 1;">
                        <span style="font-size: 0.85rem; color: var(--text-secondary); font-weight: 600; white-space: nowrap;">Type:</span>
                        <select class="dict-term-type input-control" style="width: 120px; padding: 0.25rem 0.5rem; font-size: 0.85rem;">
                            <option value="countable" ${type === 'countable' ? 'selected' : ''}>Countable</option>
                            <option value="plural" ${type === 'plural' ? 'selected' : ''}>Plural</option>
                            <option value="mass" ${type === 'mass' ? 'selected' : ''}>Mass Noun</option>
                        </select>
                        <span style="font-size: 0.85rem; color: var(--text-secondary); font-weight: 600; white-space: nowrap;">Unit/Prefix:</span>
                        <input type="text" class="dict-term-unit input-control" placeholder="E.g. bottle of" value="${escapeHtml(unit)}" style="width: 150px; padding: 0.25rem 0.5rem; font-size: 0.85rem;">
                        <button class="dict-term-del btn" style="padding: 0.35rem 0.60rem; background: rgba(255, 70, 70, 0.15); border-color: rgba(255, 70, 70, 0.25); color: rgb(255, 100, 100); font-weight: bold; font-size: 0.95rem;">&times;</button>
                    `;
                    
                    const input = row.querySelector('.dict-term-input');
                    const select = row.querySelector('.dict-term-type');
                    const unitInput = row.querySelector('.dict-term-unit');
                    
                    const updateProps = () => {
                        const nName = input.value.trim();
                        const nType = select.value;
                        const nUnit = unitInput.value.trim();
                        if (nUnit) {
                            list[idx] = [nName, nType, nUnit];
                        } else {
                            list[idx] = [nName, nType];
                        }
                        updateTotalFortunesCount();
                    };
                    
                    input.addEventListener('change', updateProps);
                    select.addEventListener('change', updateProps);
                    unitInput.addEventListener('change', updateProps);
                } else {
                    row.innerHTML = `
                        <span style="font-size: 0.85rem; color: var(--text-secondary); font-weight: 600; white-space: nowrap;">Term:</span>
                        <input type="text" class="dict-term-input input-control" value="${escapeHtml(termName)}" style="flex-grow: 1;">
                        <button class="dict-term-del btn" style="padding: 0.35rem 0.60rem; background: rgba(255, 70, 70, 0.15); border-color: rgba(255, 70, 70, 0.25); color: rgb(255, 100, 100); font-weight: bold; font-size: 0.95rem;">&times;</button>
                    `;
                    
                    const input = row.querySelector('.dict-term-input');
                    input.addEventListener('change', () => {
                        list[idx] = input.value.trim();
                        updateTotalFortunesCount();
                    });
                }

                // Handle deletes
                row.querySelector('.dict-term-del').addEventListener('click', () => {
                    list.splice(idx, 1);
                    renderCategoryTerms(key); // redraw grid
                    updateTotalFortunesCount();
                });

                grid.appendChild(row);
            });

            card.appendChild(grid);
            elDictViewContainer.appendChild(card);

            // Add listener
            document.getElementById('btn-dict-bulk-add').addEventListener('click', () => {
                const addInput = document.getElementById('dict-bulk-add-input');
                const val = addInput.value.trim();
                if (val) {
                    const exists = list.some(item => (Array.isArray(item) ? item[0] : item) === val);
                    if (!exists) {
                        const isTupleCategory = [
                            'PEOPLE_SUBJECT', 'CREATURE_SUBJECT', 'ACTIVE_DEVICE', 
                            'BENCH_TOOL', 'SOCIAL_OBJECT', 'ABSURD_OBJECT', 
                            'TECH_ITEM', 'CRAFT_ITEM'
                        ].includes(key) || (list.length > 0 && Array.isArray(list[0]));
                        
                        if (isTupleCategory) {
                            list.push([val, "countable"]);
                        } else {
                            list.push(val);
                        }
                        renderCategoryTerms(key);
                        updateTotalFortunesCount();
                    }
                }
            });
        }

        elBtnSaveAllDict.addEventListener('click', () => {
            saveConfig().then(() => alert('Successfully saved dictionary changes back to fortunes.py!'));
        });

        // Templates tab functions
        function renderTemplatesTab() {
            renderTemplateList(config.UPBEAT_TEMPLATES, elUpbeatTemplatesList, 'upbeat');
            renderTemplateList(config.OMINOUS_TEMPLATES, elOminousTemplatesList, 'ominous');
        }

        function renderTemplateList(templates, elTargetList, type) {
            elTargetList.innerHTML = '';
            templates.forEach((tpl, idx) => {
                const row = document.createElement('div');
                row.className = 'template-item-row';
                row.id = `template-item-${type}-${idx}`;
                row.style.display = 'flex';
                row.style.flexDirection = 'column';
                row.style.gap = '0.5rem';
                row.style.alignItems = 'stretch';
                row.innerHTML = `
                    <div style="display: flex; align-items: flex-start; gap: 0.5rem;">
                        <span style="font-family: var(--font-display); font-size: 0.8rem; opacity: 0.6; min-width: 20px; margin-top: 0.4rem;">#${idx+1}</span>
                        <textarea class="template-textarea" data-index="${idx}" style="min-height: 70px; flex-grow: 1; padding: 0.5rem; font-size: 0.9rem; line-height: 1.4; border: 1px solid rgba(255,255,255,0.08); border-radius: 6px; background: rgba(0,0,0,0.2);">${escapeHtml(tpl)}</textarea>
                    </div>
                    <div style="display: flex; justify-content: flex-end; gap: 0.5rem; padding-left: 28px;">
                        <button class="btn btn-preview" style="padding: 0.25rem 0.6rem; font-size: 0.8rem; background: rgba(0, 240, 255, 0.1); border-color: rgba(0, 240, 255, 0.25); color: var(--accent-cyan);" data-index="${idx}">🔮 Preview 100</button>
                        <button class="btn btn-delete" style="padding: 0.25rem 0.6rem; font-size: 0.8rem; background: rgba(255, 70, 70, 0.1); border-color: rgba(255, 70, 70, 0.25); color: rgb(255, 100, 100);" data-index="${idx}">Remove</button>
                    </div>
                `;

                const txt = row.querySelector('.template-textarea');
                txt.addEventListener('change', () => {
                    templates[idx] = txt.value.trim();
                    updateTotalFortunesCount();
                });

                row.querySelector('.btn-preview').addEventListener('click', () => {
                    openTemplatePreviewsModal(templates[idx]);
                });

                row.querySelector('.btn-delete').addEventListener('click', () => {
                    templates.splice(idx, 1);
                    renderTemplateList(templates, elTargetList, type);
                    updateTotalFortunesCount();
                });

                elTargetList.appendChild(row);
            });
        }

        elBtnAddUpbeatTemplate.addEventListener('click', () => {
            config.UPBEAT_TEMPLATES.push("A new template about {ITEM} or {VILLAGE}.");
            renderTemplateList(config.UPBEAT_TEMPLATES, elUpbeatTemplatesList, 'upbeat');
            updateTotalFortunesCount();
        });

        elBtnAddOminousTemplate.addEventListener('click', () => {
            config.OMINOUS_TEMPLATES.push("Beware of {HAZARD} when compiling code for {ACTIVE_DEVICE}.");
            renderTemplateList(config.OMINOUS_TEMPLATES, elOminousTemplatesList, 'ominous');
            updateTotalFortunesCount();
        });

        elBtnSaveAllTemplates.addEventListener('click', () => {
            saveConfig().then(() => alert('Successfully saved all templates changes back to fortunes.py!'));
        });

        // Helper functions for template permutations
        function extractPlaceholders(template) {
            const regex = /\{([A-Z_]+)\}/g;
            let matches = [];
            let match;
            while ((match = regex.exec(template)) !== null) {
                matches.push(match[1]);
            }
            return matches;
        }

        function getCategoryVariationsCount(list) {
            let len = 0;
            list.forEach(item => {
                if (Array.isArray(item)) {
                    const itype = item[1];
                    const unit = item[2];
                    if (itype === 'plural' && !unit) {
                        len += 1 + COLLECTIVE_PREFIXES_JS.length; // 1 (no prefix) + 9 (prefixes) = 10
                    } else {
                        len += 1;
                    }
                } else {
                    len += 1;
                }
            });
            return len;
        }

        function getCategoryUniquePermutationsCount(list, M) {
            if (M === 0) return 1;
            const N = list.length;
            if (M > N) {
                let singleCount = 0;
                list.forEach(item => {
                    if (Array.isArray(item)) {
                        const itype = item[1];
                        const unit = item[2];
                        if (itype === 'plural' && !unit) {
                            singleCount += 1 + COLLECTIVE_PREFIXES_JS.length;
                        } else {
                            singleCount += 1;
                        }
                    } else {
                        singleCount += 1;
                    }
                });
                return Math.pow(singleCount, M);
            }

            const V = list.map(item => {
                if (Array.isArray(item)) {
                    const itype = item[1];
                    const unit = item[2];
                    if (itype === 'plural' && !unit) {
                        return 1 + COLLECTIVE_PREFIXES_JS.length;
                    } else {
                        return 1;
                    }
                } else {
                    return 1;
                }
            });

            let dp = Array(M + 1).fill(0);
            dp[0] = 1;
            for (let i = 0; i < V.length; i++) {
                const val = V[i];
                for (let j = M; j >= 1; j--) {
                    dp[j] = dp[j] + dp[j - 1] * val;
                }
            }

            let fact = 1;
            for (let i = 1; i <= M; i++) {
                fact *= i;
            }
            return dp[M] * fact;
        }

        function getTemplatePermutationsCount(template, placeholders) {
            if (placeholders.length === 0) return 1;

            const counts = {};
            placeholders.forEach(ph => {
                counts[ph] = (counts[ph] || 0) + 1;
            });

            let totalCount = 1;

            for (const ph in counts) {
                const M = counts[ph];
                let list = [];
                if (ph === 'MAP_LOCATION') {
                    list = Array(config.MAP_LOCATIONS.length).fill(1);
                } else if (ph === 'VILLAGE') {
                    list = Array(config.VILLAGES.length).fill(1);
                } else if (ph === 'DESTINATION') {
                    list = Array(config.MAP_LOCATIONS.length + config.VILLAGES.length).fill(1);
                } else if (ph === 'TECH_ADJECTIVE_ITEM') {
                    const len = (config.TERMS['TECH_ADJECTIVE'] || []).length * getCategoryVariationsCount(config.TERMS['TECH_ITEM'] || []);
                    list = Array(len).fill(1);
                } else if (ph === 'CRAFT_ADJECTIVE_ITEM') {
                    const len = (config.TERMS['CRAFT_ADJECTIVE'] || []).length * getCategoryVariationsCount(config.TERMS['CRAFT_ITEM'] || []);
                    list = Array(len).fill(1);
                } else if (ph === 'TECH_SHINY_ITEM') {
                    const len = getCategoryVariationsCount(config.TERMS['TECH_ITEM'] || []);
                    list = Array(len).fill(1);
                } else if (ph === 'TECH_RARE_ITEM') {
                    const len = getCategoryVariationsCount(config.TERMS['TECH_ITEM'] || []);
                    list = Array(len).fill(1);
                } else {
                    list = config.TERMS[ph] || [];
                }

                totalCount *= getCategoryUniquePermutationsCount(list, M);
            }

            return totalCount;
        }

        function formatVillageJS(name) {
            let name_lower = name.toLowerCase().trim();
            let proper_noun_exceptions = ["milliways", "bodgeham-on-wye", "glastonledburyshire-on-severn", "sheffield-by-the-sea"];
            if (proper_noun_exceptions.includes(name_lower)) {
                return `"${name}"`;
            }
            let self_descriptive_words = [
                "hackspace", "hacklab", "makespace", "makerspace", "make space", "maker space",
                "consulate", "embassy", "village", "sector", "camp", "lounge", "area", "house", 
                "room", "hq", "lab", "division", "station", "centre", "center", "ville"
            ];
            if (self_descriptive_words.some(word => name_lower.includes(word))) {
                return `"${name}"`;
            }
            let collective_nouns = ["club", "armada", "commission", "society", "project", "team", "group", "network", "force", "consortium", "union", "association", "friends", "bods", "racers", "pals", "gamers", "makers", "biohackers"];
            if (collective_nouns.some(noun => name_lower.endsWith(noun))) {
                return `the "${name}" village`;
            }
            return `the village "${name}"`;
        }

        function fixAAnJS(text) {
            let vowels = "aeiouAEIOU";
            let words = text.split(" ");
            for (let i = 0; i < words.length - 1; i++) {
                if (words[i] === "a" || (i === 0 && words[i] === "A")) {
                    let clean_next = words[i+1].replace(/^[`"'(]+/, "");
                    if (clean_next && vowels.includes(clean_next[0])) {
                        words[i] = (words[i] === "A") ? "An" : "an";
                    }
                }
            }
            return words.join(" ");
        }

        function updateTotalFortunesCount() {
            let totalUpbeat = 0;
            config.UPBEAT_TEMPLATES.forEach(tpl => {
                const placeholders = extractPlaceholders(tpl);
                totalUpbeat += getTemplatePermutationsCount(tpl, placeholders);
            });

            let totalOminous = 0;
            config.OMINOUS_TEMPLATES.forEach(tpl => {
                const placeholders = extractPlaceholders(tpl);
                totalOminous += getTemplatePermutationsCount(tpl, placeholders);
            });

            const totalPool = totalUpbeat + totalOminous;
            const elStat = document.getElementById('stat-total-fortunes');
            if (elStat) {
                elStat.innerText = totalPool.toLocaleString();
            }
        }
    </script>
</body>
</html>
"""

def main():
    # Setup server
    port = 8080
    host = "localhost"
    
    server_address = (host, port)
    
    try:
        httpd = http.server.HTTPServer(server_address, SimulatorRequestHandler)
    except OSError:
        # Port is already busy, find another free port
        port = find_free_port()
        server_address = (host, port)
        httpd = http.server.HTTPServer(server_address, SimulatorRequestHandler)

    url = f"http://{host}:{port}/"
    print("=" * 60)
    try:
        print(f"🔮 Fortune Teller Simulator is running on: {url}")
    except UnicodeEncodeError:
        print(f"[*] Fortune Teller Simulator is running on: {url}")
    print("Close this terminal window or press Ctrl+C to stop the simulator.")
    print("=" * 60)
    
    # Auto-open browser tab
    webbrowser.open_new_tab(url)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Fortune Teller Simulator server...")
        httpd.server_close()
        sys.exit(0)

if __name__ == "__main__":
    main()
