#!/usr/bin/env python3
import sys
import os
import urllib.parse
import json
import webbrowser
import http.server
import socket
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
        elif path == "/":
            self.handle_home()
        else:
            self.send_error(404, "File not found")

    def handle_api_fortunes(self, query):
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
                path_seed = base_seed + color_idx * 17 + number * 31
                fortune_text = fortunes.generate_fortune(path_seed)
                paths.append({
                    "color_idx": color_idx,
                    "color_name": color_name,
                    "color_rgb": color_rgb,
                    "number": number,
                    "path_seed": path_seed,
                    "fortune": fortune_text
                })
                
        # 3. Generate sequential random fortunes from seed
        sequential = []
        seq_rng = fortunes.SeededRandom(base_seed)
        for i in range(100):
            step_seed = seq_rng.next_int()
            fortune_text = fortunes.generate_fortune(step_seed)
            sequential.append({
                "index": i + 1,
                "seed": step_seed,
                "fortune": fortune_text
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
    <title>🔮 Tildagon Fortune Teller Reviewer</title>
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
            max-width: 600px;
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
            padding: 0 2px;
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
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header>
            <h1>🔮 Tildagon Fortune Teller Reviewer</h1>
            <p>Seeded Fortune Generator & Simulator. Easily review badge fortunes, custom seeds, daily combinations, and bulk outcomes.</p>
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
                    </div>

                    <!-- Filters & Actions -->
                    <div class="toolbar">
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

            </div>

        </div>

        <!-- Footer Info -->
        <footer>
            <p>Tildagon Fortune Teller Simulator • Seeded deterministic choices. Formula matches client micro-python files.</p>
            <p style="margin-top: 0.25rem; opacity: 0.7;">Total template formulas: 30 • Total possible distinct combinations: 8,122,802</p>
        </footer>
    </div>

    <!-- Scripting -->
    <script>
        let currentData = null;
        let activeTab = 'paths';

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
        
        const elColorsGrid = document.getElementById('colors-grid');
        const elSeqList = document.getElementById('seq-list');

        // Set default date to today
        const todayStr = new Date().toISOString().split('T')[0];
        elDateInput.value = todayStr;

        // Init loads
        document.addEventListener('DOMContentLoaded', () => {
            loadFromToday();
        });

        // Event Listeners
        elBtnRandom.addEventListener('click', () => {
            const randSeed = Math.floor(Math.random() * 2147483647);
            elSeedInput.value = randSeed;
            fetchFortunes({ seed: randSeed });
        });

        elBtnToday.addEventListener('click', () => {
            loadFromToday();
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
                // Reload using the current seed without theme manual override
                fetchFortunes({ seed: elSeedInput.value });
            } else {
                elManualThemeGroup.style.opacity = '1';
                elManualThemeGroup.style.pointerEvents = 'auto';
                
                // Set theme 0 active by default on manual switch, and reload
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
                
                if (tab === 'paths') {
                    document.getElementById('tab-paths').classList.remove('hidden');
                    document.getElementById('tab-sequential').classList.add('hidden');
                } else {
                    document.getElementById('tab-paths').classList.add('hidden');
                    document.getElementById('tab-sequential').classList.remove('hidden');
                }
                
                filterResults();
            });
        });

        elSearchInput.addEventListener('input', () => {
            filterResults();
        });

        elBtnExport.addEventListener('click', () => {
            exportToMarkdown();
        });

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

        function renderBadgePaths(paths) {
            elColorsGrid.innerHTML = '';
            
            // Group by color index
            const groups = {};
            paths.forEach(p => {
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

                colorPaths.forEach(p => {
                    const item = document.createElement('div');
                    item.className = 'fortune-item';
                    item.style.setProperty('--btn-color', rgbStr);
                    
                    item.innerHTML = `
                        <div class="fortune-number">${p.number}</div>
                        <div class="fortune-text-box">
                            <span class="fortune-text">${p.fortune}</span>
                            <span class="fortune-meta">seed: ${p.path_seed}</span>
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
            sequential.forEach(s => {
                const item = document.createElement('div');
                item.className = 'seq-item';
                item.innerHTML = `
                    <div class="seq-badge">#${s.index}</div>
                    <div class="seq-content">
                        <div class="fortune-text">${s.fortune}</div>
                        <div class="seq-seed">Seed: ${s.seed}</div>
                    </div>
                `;
                elSeqList.appendChild(item);
            });
        }

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
                const items = elColorsGrid.querySelectorAll('.fortune-item');
                const cards = elColorsGrid.querySelectorAll('.color-card');
                
                cards.forEach(card => {
                    let hasVisibleItem = false;
                    const cItems = card.querySelectorAll('.fortune-item');
                    
                    cItems.forEach(item => {
                        const txtBox = item.querySelector('.fortune-text');
                        const origText = txtBox.textContent;
                        
                        if (!query) {
                            item.classList.remove('hidden');
                            txtBox.innerHTML = origText; // clear highlights
                            hasVisibleItem = true;
                        } else if (origText.toLowerCase().includes(query)) {
                            item.classList.remove('hidden');
                            txtBox.innerHTML = highlightText(origText, query);
                            hasVisibleItem = true;
                        } else {
                            item.classList.add('hidden');
                        }
                    });

                    // Hide the parent card if it has no visible items
                    if (hasVisibleItem) {
                        card.classList.remove('hidden');
                    } else {
                        card.classList.add('hidden');
                    }
                });
            } else {
                const items = elSeqList.querySelectorAll('.seq-item');
                items.forEach(item => {
                    const txtBox = item.querySelector('.fortune-text');
                    const origText = txtBox.textContent;
                    
                    if (!query) {
                        item.classList.remove('hidden');
                        txtBox.innerHTML = origText;
                    } else if (origText.toLowerCase().includes(query)) {
                        item.classList.remove('hidden');
                        txtBox.innerHTML = highlightText(origText, query);
                    } else {
                        item.classList.add('hidden');
                    }
                });
            }
        }

        function highlightText(text, keyword) {
            const regex = new RegExp(`(${escapeRegExp(keyword)})`, 'gi');
            return text.replace(regex, '<span class="highlight">$1</span>');
        }

        function escapeRegExp(string) {
            return string.replace(/[.*+?^${}()|[\]\\\\]/g, '\\\\$&');
        }

        function exportToMarkdown() {
            if (!currentData) return;

            let md = `# Tildagon Fortune Teller Review Report\\n\\n`;
            md += `* **Generated on:** ${new Date().toLocaleString()}\\n`;
            md += `* **Base Seed:** ${currentData.seed}\\n`;
            md += `* **Theme Index:** ${currentData.theme_idx} (${currentData.theme_mode === 'auto' ? 'Calculated' : 'Manual Overridden'})\\n`;
            md += `* **Date Context:** ${currentData.date}\\n`;
            md += `* **Badge ID:** ${currentData.badge_id}\\n\\n`;
            
            md += `## 36 Path Fortunes (By Badge Colors/Buttons)\\n\\n`;
            
            const groups = {};
            currentData.paths.forEach(p => {
                if (!groups[p.color_idx]) groups[p.color_idx] = [];
                groups[p.color_idx].push(p);
            });

            for (let i = 0; i < 6; i++) {
                const colPaths = groups[i];
                if (!colPaths) continue;
                md += `### Corner ${i + 1} - ${colPaths[0].color_name} (${getCornerLabel(i + 1)})\\n\\n`;
                colPaths.forEach(p => {
                    md += `* **Number ${p.number}:** ${p.fortune} *(path seed: ${p.path_seed})*\\n`;
                });
                md += `\\n`;
            }

            md += `## First 20 Sequential Outcomes\\n\\n`;
            for (let i = 0; i < 20; i++) {
                const s = currentData.sequential[i];
                md += `${s.index}. ${s.fortune} *(seed: ${s.seed})*\\n`;
            }

            // Copy to clipboard
            navigator.clipboard.writeText(md).then(() => {
                alert("Copied Review Report in Markdown format to clipboard!");
            }).catch(err => {
                console.error("Clipboard copy failed: ", err);
                // Fallback to text file download
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
    print(f"🔮 Fortune Teller Simulator is running on: {url}")
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
