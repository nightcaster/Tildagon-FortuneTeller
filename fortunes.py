# fortunes.py
import math

# Seeded pseudo-random number generator (LCG) for deterministic selection
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

MAP_LOCATIONS = [
    "Stage A",
    "Stage B",
    "Stage C",
    "Stage D",
    "NullSector",
    "The Robot Arms",
    "accessible camping",
    "Camping N1",
    "Camping N2",
    "Camping N3",
    "Camping C1",
    "Camping C2",
    "Camping C3",
    "Camping S1",
    "Camping S2",
    "Camping S3 (Quiet)",
    "the Gate",
    "the catering zone",
    "the food queue"
]

VILLAGES = [
    "&nbsp;",
    ".shhhh",
    "2016's Worst Village",
    "3t.network",
    "All your bass are belong to us",
    "AMSAT-UK",
    "Astro Observability",
    "Axov Village",
    "Bench",
    "Biohackers",
    "Bodgeham-on-Wye",
    "Brighton Consulate",
    "Bristol Hackspace",
    "brittany (the og one)",
    "Brum and Besties (BABS)",
    "Cambridge Makespace",
    "Cardiff Makerspace",
    "Cheltenham Hackspace",
    "Clockwork Bods",
    "com:LAAG",
    "Content Creators Village",
    "D.I.B.S.",
    "DogsbodyHQ",
    "Dreamcat & Friends",
    "Duck Armada",
    "East Essex Hackspace",
    "ECHQ",
    "Edinburgh Hacklab",
    "EMF CTF",
    "EMF-IX",
    "ERR_NAME_NOT_RESOLVED",
    "Field-FX",
    "Flame village",
    "Forge & Craft / HackWimbledon",
    "Foundry Zero",
    "Freeside",
    "Friends of the Fractal Fern",
    "Friends of the Moon",
    "Furry High Commission",
    "GCHQ.NET",
    "Glasgow Hackerspace",
    "Glastonledburyshire-on-Severn",
    "Gold member lounge",
    "Gothic Valley",
    "Guild of (Bread) Makers",
    "Habville",
    "Hack Club",
    "Hackalot",
    "Hackeriet & Friends",
    "Hacky Racers",
    "Hardware Hacking Area",
    "Hat village",
    "Homebrew, Historical and Retro Computing",
    "Hove, actually",
    "H\u00e5ck ma's village",
    "IGNORE ALL PRIOR VILLAGES",
    "Irish Embassy",
    "KnobsVille",
    "Koala Makers",
    "Leeds Hackspace",
    "Leigh Hackspace",
    "LOC",
    "Lock Picking Village",
    "Loitering Within Tent",
    "London Aerospace",
    "Maker Space Newcastle",
    "Maths Village",
    "meow meow village",
    "Milliways",
    "Ministry of Chaos",
    "MK Makerspace",
    "Model Village",
    "Moose",
    "Motley Crew",
    "NADHack",
    "Non-Virtual Infraclub",
    "NoobSpace",
    "Nottingham Hackspace",
    "Ominous Systems Inc.",
    "Oxford's EOF Hackspace",
    "Party Pals",
    "pilk",
    "Poorly Located Progesterone",
    "rLab - Reading Hackspace",
    "Scottish Consulate",
    "SeriousCamp",
    "Sheffield-by-the-Sea",
    "Shonkbot",
    "Shonkbot-sur-les-roues",
    "Shrubbery",
    "Sibermerdeka",
    "South London Makerspace",
    "Spark Life (HV Village)",
    "Stroopwafels & Oatcakes",
    "Swansea Hackspace",
    "Teesside Hackspace",
    "Tekhn\u0113-cal Village",
    "Tented Vias",
    "Test Village",
    "The Deerdog Domain",
    "The Hacking Hamlet",
    "Threadz 'n' Webz",
    "Traditional Crafts",
    "Tricky Disco",
    "Unaffiliated Village",
    "Unnamed Village",
    "Village of Certain Doom",
    "York Hackspace",
    "ZTL"
]

TERMS = {
    "MAP_LOCATION": MAP_LOCATIONS,
    "VILLAGE": VILLAGES,
    "DESTINATION": MAP_LOCATIONS + VILLAGES,
    "PEOPLE_SUBJECT": [
        ("friend", "countable"),
        ("friends", "plural"),
        ("volunteer", "countable"),
        ("volunteers", "plural"),
        ("furry", "countable"),
        ("furries", "plural"),
        ("hacker", "countable"),
        ("hackers", "plural"),
        ("hardware wizard", "countable"),
        ("hardware wizards", "plural"),
        ("duck", "countable"),
        ("ducks", "plural"),
        ("event sponsor", "countable"),
        ("event sponsors", "plural"),
        ("Null Sector DJ", "countable"),
        ("Null Sector DJs", "plural"),
        ("event organizer", "countable"),
        ("event organizers", "plural"),
    ],
    "CREATURE": [
        ("robot", "countable"),
        ("creature", "countable"),
        ("duck", "countable"),
        ("ducks", "plural"),
        ("spider", "countable"),
        ("spiders", "plural"),
        ("spider wearing a tiny high-vis vest", "countable"),
        ("spiders wearing tiny high-vis vests", "plural"),
        ("GPS rave bots", "plural"),
        ("hexpansions", "plural"),
        ("volunteers", "plural"),
        ("rogue deer", "plural"),
    ],
    "COMPUTE_VERB": [
        "debug",
        "program",
        "optimize",
        "reverse engineer",
        "analyse",
    ],
    "HARDWARE_VERB": [
        "solder",
        "repair",
        "upgrade",
        "reverse engineer",
        "overclock",
        "re-solder",
    ],
    "SOCIAL_VERB": [
        "trade with",
        "spill a drink on",
        "buy a drink for",
        "discover",
        "find",
        "misplace",
    ],
    "ACTIVE_DEVICE": [
        ("Tildagon", "countable"),
        ("laptop", "countable"),
        ("RFID reader", "countable"),
        ("Flipper Zero", "countable"),
        ("microcontroller", "countable"),
    ],
    "BENCH_TOOL": [
        ("solder station", "countable"),
        ("oscilloscope", "countable"),
        ("3D printer", "countable"),
        ("Tesla coil", "countable"),
        ("amateur radio", "countable"),
        ("Wi-Fi antenna", "countable"),
        ("soldering iron", "countable"),
    ],
    "COMPUTE_TARGET": [
        "someone else's badge",
        "some sketchy firmware",
        "a hidden easter egg",
        "an ancient floppy disk",
        "an arcade machine",
        "a game cartridge",
    ],
    "HARDWARE_TARGET": [
        "a custom PCB",
        "a tiny IC",
        "a GPS tracker",
        "a prototype hexpansion",
        "an overpowered microcontroller",
        "an oscilloscope",
        "a prototype Tildagon frontboard",
        "a digital synth",
        "an unfinished hexpansion",
    ],
    "SOCIAL_OBJECT": [
        ("cold beverage", "countable"),
        ("badge addon", "countable"),
        ("duck", "countable"),
        ("dynamic token", "countable"),
    ],
    "ABSURD_OBJECT": [
        ("duck", "countable"),
        ("bratwurst", "countable"),
        ("dynamic token", "countable"),
        ("LED strip woven into a hammock", "countable"),
        ("solder flux", "mass", "tube of"),
    ],
    "CAMP_ACTION": [
        "volunteer at the bar",
        "take a break",
        "go on an adventure",
        "sleep for 8 hours",
        "attend a talk on retro computing",
        "stay up all night coding",
    ],
    "CAMP_ACTION_ACTIVE": [
        "volunteering at the bar",
        "taking a break",
        "going on an adventure",
        "sleeping for 8 hours",
        "attending a talk on retro computing",
        "staying up all night coding",
    ],
    "HACKER_ACTION": [
        "take a risk",
        "solve a difficult puzzle",
        "start a side project",
        "learn lockpicking",
        "explore the campsite network",
        "solder some SMD components",
        "tinker with high-voltage gear",
        "exchange rare electronic parts",
        "write firmware in MicroPython",
        "repair retro arcade games",
        "configure a custom gateway",
    ],
    "HAZARD": [
        "loose solder joints",
        "unsecured tents",
        "high powered lasers",
        "roaming gps rave bots",
        "spiders in the camp",
        "infinite loops",
        "poorly crimped cables",
        "RF interference",
        "memory leaks",
        "sudden power cuts",
        "overheated soldering irons",
        "depleted badge batteries",
        "unlabeled USB sticks",
        "rogue DHCP servers",
        "over-caffeinated hackers",
    ],
    "TECH_ADJECTIVE": [
        "flashing",
        "digital",
        "glowing",
        "cybernetic",
        "clandestine",
        "mysterious",
        "analog",
        "overclocked",
        "deprecated",
        "quantum-entangled",
        "ultra-bright",
        "waterproof",
        "totally useless",
        "ultra rare",
    ],
    "CRAFT_ADJECTIVE": [
        "copper-plated",
        "clandestine",
        "mysterious",
        "waterproof",
        "glowing",
        "red hot",
        "sopping wet",
        "totally useless",
        "really beautiful",
        "highly sought-after",
    ],
    "TECH_ITEM": [
        ("badge addon", "countable"),
        ("firmware update", "countable"),
        ("USB drive", "countable"),
        ("LED strip", "countable"),
        ("oscilloscope", "countable"),
        ("custom PCB", "countable"),
        ("RF antenna", "countable"),
        ("solder", "mass", "spool of"),
        ("fiber optic cable", "mass", "length of"),
        ("thermal paste", "mass", "dollop of"),
        ("resistors", "plural", "strip of"),
    ],
    "CRAFT_ITEM": [
        ("solder joint", "countable"),
        ("duck", "countable"),
        ("cup of tea", "countable"),
        ("crimp tool", "countable"),
        ("component bag", "countable"),
        ("soldering flux", "mass", "roll of"),
        ("jumper wire", "countable"),
        ("conductive thread", "mass", "bobbin of"),
        ("club mate", "mass", "bottle of"),
        ("hot glue", "mass", "stick of"),
        ("felt", "mass", "sheet of"),
    ],
    "TECH_TRIVIA": [
        "solder joints",
        "firmware updates",
        "memory leaks",
        "GPIO pins",
        "custom PCBs",
        "RF frequencies",
        "hexpansions",
        "BGP routing tables",
        "SMD soldering techniques",
        "MicroPython garbage collection",
        "Fourier transforms",
        "packet switching protocols",
    ],
    "TIME": [
        "at midnight",
        "during the opening talk",
        "before the closing ceremony",
        "at dawn",
        "during the next power cut",
        "under the cover of darkness",
        "while volunteering",
        "after the second beer",
        "at exactly 0x4141 ticks",
        "during the next badge firmware update",
        "during a heavy downpour",
        "before your next selfie",
    ],
    "LUCKY_NUMBER": [
        "seven",
        "thirteen",
        "forty-two",
        "eighty-eight",
        "0x4141",
        "1337",
        "65535",
        "three",
        "twenty-six",
        "0xCAFE",
        "four hundred and four",
        "eight thousand and eighty",
    ],
    "SPECIAL_DEVICE_FEATURE": [
        "infinite battery life",
        "root access",
        "the spider repellent ability",
        "optical camouflage",
        "the ability to boil water",
    ],
    "VISIT_TYPE": [
        "a walk around",
        "an amble towards",
        "a gentle stroll past",
        "a quick run around",
        "a late-night wander near",
        "a brief march past",
        "a session at",
        "a visit to",
        "a few drinks at",
    ],
    "CAMPING_ITEM": [
        ("your socks", "mass"),
        ("your sleeping bag", "mass"),
        ("your airbed", "mass"),
        ("your tent", "mass"),
        ("your camping chair", "mass"),
        ("your backpack", "mass"),
    ],
    "CAMPING_LOCATION": [
        ("inside your socks", "mass"),
        ("in the depth of your sleeping bag", "mass"),
        ("in the bowels of your tent", "mass"),
        ("in the queue for the showers", "mass"),
        ("in the toilets", "mass"),
        ("in the bar", "mass"),
        ("in the info tent", "mass"),
    ],
    "FESTIVAL_INFRASTRUCTURE": [
        ("the DECT phone system", "mass"),
        ("the fibre backbone", "mass"),
        ("stuck telehandler", "countable"),
        ("stuck van", "countable"),
        ("the Wi-Fi infrastructure", "mass"),
        ("a soiled Datenklo", "mass"),
    ],
}

UPBEAT_TEMPLATES = [
    "{PEOPLE_SUBJECT} will {SOCIAL_VERB} {CREATURE}.",
    "Try {CAMP_ACTION_ACTIVE} at {DESTINATION}.",
    "Your code will finally compile after {VISIT_TYPE} {MAP_LOCATION}.",
    "{CREATURE_PLURAL_COLLECTIVE} riding {CREATURE_PLURAL} will bring great fortune to {VILLAGE}.",
    "{PEOPLE_SUBJECT_COLLECTIVE} will {CAMP_ACTION} .",
    "{VISIT_TYPE} {VILLAGE} will inspire you to {CAMP_ACTION}.",
    "You will discover {TECH_ADJECTIVE_ITEM} while trying to {HACKER_ACTION}.",
    "You will discover {CRAFT_ADJECTIVE_ITEM} while trying to {HACKER_ACTION}.",
    "Your {ACTIVE_DEVICE} will flawlessly {COMPUTE_VERB} {COMPUTE_TARGET}.",
    "While trying to {HACKER_ACTION} at {DESTINATION}, {ABSURD_OBJECT} will appear.",
    "You will meet {PEOPLE_SUBJECT_COLLECTIVE} who will help you {HACKER_ACTION}.",
    "To {CAMP_ACTION}, you must first find {TECH_ADJECTIVE_ITEM}.",
    "To {CAMP_ACTION}, you must first obtain {CRAFT_ADJECTIVE_ITEM}.",
    "If you {CAMP_ACTION} {TIME}, you might find {TECH_ADJECTIVE_ITEM}.",
    "If you {CAMP_ACTION} {TIME}, you might create {CRAFT_ADJECTIVE_ITEM}.",
    "A talk about {TECH_TRIVIA} will explain how to easily {HACKER_ACTION}.",
    "You will find luck when you {COMPUTE_VERB} {COMPUTE_TARGET}.",
    "Fortune awaits when you {HARDWARE_VERB} {HARDWARE_TARGET}.",
    "{PEOPLE_SUBJECT} at {DESTINATION} will offer you {TECH_SHINY_ITEM} in exchange for debugging assistance.",
    "Your {BENCH_TOOL} will work better near {VILLAGE}.",
    "If you visit {DESTINATION} {TIME}, you might {PEOPLE_SUBJECT} {CAMP_ACTION}.",
    "{PEOPLE_SUBJECT} at {DESTINATION} will help you {HACKER_ACTION}.",
    "To trade {TECH_RARE_ITEM} with {PEOPLE_SUBJECT}, you should visit {DESTINATION}.",
    "A session at {VILLAGE} will teach you all about {TECH_TRIVIA}.",
    "Your luckiest number is {LUCKY_NUMBER} and your luckiest item is {TECH_ADJECTIVE_ITEM}.",
    "Your luckiest number is {LUCKY_NUMBER} and your luckiest item is {CRAFT_ADJECTIVE_ITEM}.",
    "A mysterious friendly signal at {DESTINATION} suggests you should immediately {CAMP_ACTION}.",
    "You will spot Jonty fixing {FESTIVAL_INFRASTRUCTURE} using {CREATURE_PLURAL_COLLECTIVE}.",
    "A mysterious firmware update signed by Jonty will grant your {ACTIVE_DEVICE} {SPECIAL_DEVICE_FEATURE}.",
    "A ping on port 8081 {TIME} signals incoming {CREATURE_PLURAL}",
    "Be on the lookout for {HARDWARE_TARGET} to {HARDWARE_VERB}",
    "Quick! You should be {CAMP_ACTION_ACTIVE}",
    "If you like {HARDWARE_TARGET}, check {CAMPING_LOCATION}.",
    "If {CREATURE} makes eye contact, {HACKER_ACTION}.",
    "If {PEOPLE_SUBJECT?mention|mentions} Jonty, change the topic.",
    "If you see {CREATURE_PLURAL}, offer them {CAMPING_ITEM}.",
    "If you see {PEOPLE_SUBJECT}, compliment their outfit.",
    "If you see {HARDWARE_TARGET}, admire it from afar.",
    "You will find fame and fortune {CAMPING_LOCATION}.",
    "{CREATURE?are|is} not what they seem...",
    "If {PEOPLE_SUBJECT?are coding late|is coding late}, make them some tea!."
]

OMINOUS_TEMPLATES = [
    "Beware of {HAZARD} when you {CAMP_ACTION}.",
    "You will meet a new nemesis while trying to {HACKER_ACTION} at the {MAP_LOCATION}.",
    "Beware of {CREATURE_PLURAL} bearing {SOCIAL_OBJECT}.",
    "Beware of {CREATURE_PLURAL} near {DESTINATION}.",
    "Your {ACTIVE_DEVICE} will detect high levels of {HAZARD} near {DESTINATION}.",
    "To avoid {HAZARD}, you should quickly {CAMP_ACTION}.",
    "You will accidentally drop your beloved {ACTIVE_DEVICE}. Butter fingers.",
    "{TIME}, you will spend hours attempting to explain {TECH_TRIVIA} to {CREATURE}.",
    "A mysterious flashing LED at {DESTINATION} is actually an ominous message about {TECH_TRIVIA}.",
    "Your {ACTIVE_DEVICE} will fail due to {HAZARD}.",
    "You will accidentally trade your {ACTIVE_DEVICE} for {TECH_ADJECTIVE_ITEM}.",
    "You will accidentally trade your {ACTIVE_DEVICE} for {CRAFT_ADJECTIVE_ITEM}.",
    "Beware of {CREATURE} trying to {COMPUTE_VERB} your unprotected {ACTIVE_DEVICE}.",
    "Beware of {CREATURE} trying to {HARDWARE_VERB} your unguarded {ACTIVE_DEVICE}.",
    "If you see {HAZARD} creeping around {DESTINATION}, take shelter at {MAP_LOCATION}.",
    "If you see Jonty sprinting toward {DESTINATION}, do not ask questions. Do not follow him.",
    "Jonty will challenge you to a game of chance behind {MAP_LOCATION}.",
    "Beware of {HAZARD} when compiling code for {ACTIVE_DEVICE}.",
    "{PEOPLE_SUBJECT} will {CAMP_ACTION} despite being advised not to.",
    "Your {ACTIVE_DEVICE} will slowly begin to resent you for not {CAMP_ACTION_ACTIVE}"
]

def format_village(name, context_before):
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
            clean_next = words[i+1].lstrip("`\"'(")
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

def format_item(adjective, item, rng=None, add_collective=False):
    if isinstance(item, (list, tuple)):
        name = item[0]
        itype = item[1]
        unit = item[2] if len(item) > 2 else None
    else:
        name = item
        itype = "countable"
        unit = None

    if itype == "plural" and not unit and rng and add_collective:
        if (rng.next_int() >> 8) % 2 == 0:
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

def _resolve_key(key):
    """
    Strip _PLURAL and/or _COLLECTIVE suffixes from a template placeholder key.
    Returns (base_key, plural_only, add_collective).

    add_collective=True  -> collective noun prefix may be randomly added (e.g. "a herd of")
    add_collective=False -> plain form, no collective prefix
    plural_only=True     -> filter TERMS list to only 'plural' typed entries

    Examples:
      "CREATURE"                   -> ("CREATURE", False, False)
      "CREATURE_PLURAL"            -> ("CREATURE", True,  False)
      "CREATURE_COLLECTIVE"        -> ("CREATURE", False, True)
      "CREATURE_PLURAL_COLLECTIVE" -> ("CREATURE", True,  True)
      "PEOPLE_SUBJECT"             -> ("PEOPLE_SUBJECT", False, False)
      "PEOPLE_SUBJECT_COLLECTIVE"  -> ("PEOPLE_SUBJECT", False, True)
    """
    add_collective = False
    plural_only = False
    if key.endswith("_COLLECTIVE"):
        key = key[:-len("_COLLECTIVE")]
        add_collective = True
    if key.endswith("_PLURAL"):
        key = key[:-len("_PLURAL")]
        plural_only = True
    return key, plural_only, add_collective

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

    active_plural = {}
    i = 0
    while True:
        idx = result.find("{", i)
        if idx == -1:
            break
        end_idx = result.find("}", idx)
        if end_idx == -1:
            break

        tag = result[idx+1:end_idx]

        if "?" in tag:
            parts = tag.split("?")
            key = parts[0]
            options = parts[1].split("|")

            base_key, plural_only, add_coll = _resolve_key(key)

            if base_key in TERMS:
                pool = [e for e in TERMS[base_key] if not plural_only or (isinstance(e, tuple) and e[1] == "plural")]
                choice = choose_unique(rng, pool or TERMS[base_key], used_terms)
                if isinstance(choice, (list, tuple)):
                    itype = choice[1]
                    choice = format_item("", choice, rng, add_collective=add_coll)
                    is_plural = (itype == "plural" and not choice.lower().startswith(("a ", "an ")))
                else:
                    choice = format_item("", choice, rng, add_collective=add_coll)
                    is_plural = False

                active_plural[base_key] = is_plural
                active_plural[base_key + "_COLLECTIVE"] = is_plural

                suffix = options[0] if is_plural else options[1] if len(options) > 1 else options[0]
                if suffix and suffix[0].isalnum():
                    val = choice + " " + suffix
                else:
                    val = choice + suffix
                result = result[:idx] + val + result[end_idx+1:]
                i = idx + len(val)
            elif key in ("MAP_LOCATION", "VILLAGE", "DESTINATION"):
                values = MAP_LOCATIONS if key == "MAP_LOCATION" else VILLAGES if key == "VILLAGE" else (MAP_LOCATIONS + VILLAGES)
                choice = choose_unique(rng, values, used_terms)
                if key == "VILLAGE" or (key == "DESTINATION" and choice in VILLAGES):
                    context_before = result[max(0, idx - 20):idx]
                    choice = format_village(choice, context_before)
                is_plural = False
                active_plural[key] = is_plural

                suffix = options[0] if is_plural else options[1] if len(options) > 1 else options[0]
                if suffix and suffix[0].isalnum():
                    val = choice + " " + suffix
                else:
                    val = choice + suffix
                result = result[:idx] + val + result[end_idx+1:]
                i = idx + len(val)
            else:
                is_plural = active_plural.get(key, False)
                verb = options[0] if is_plural else options[1] if len(options) > 1 else options[0]
                result = result[:idx] + verb + result[end_idx+1:]
                i = idx + len(verb)
        else:
            # Standard placeholder
            key = tag
            base_key, plural_only, add_coll = _resolve_key(key)

            if base_key in TERMS:
                pool = [e for e in TERMS[base_key] if not plural_only or (isinstance(e, tuple) and e[1] == "plural")]
                choice = choose_unique(rng, pool or TERMS[base_key], used_terms)
                if isinstance(choice, (list, tuple)):
                    itype = choice[1]
                    choice = format_item("", choice, rng, add_collective=add_coll)
                    is_plural = (itype == "plural" and not choice.lower().startswith(("a ", "an ")))
                else:
                    choice = format_item("", choice, rng, add_collective=add_coll)
                    is_plural = False

                active_plural[base_key] = is_plural
                active_plural[base_key + "_COLLECTIVE"] = is_plural

                result = result[:idx] + choice + result[end_idx+1:]
                i = idx + len(choice)
            elif key in ("MAP_LOCATION", "VILLAGE", "DESTINATION"):
                values = MAP_LOCATIONS if key == "MAP_LOCATION" else VILLAGES if key == "VILLAGE" else (MAP_LOCATIONS + VILLAGES)
                choice = choose_unique(rng, values, used_terms)
                if key == "VILLAGE" or (key == "DESTINATION" and choice in VILLAGES):
                    context_before = result[max(0, idx - 20):idx]
                    choice = format_village(choice, context_before)
                active_plural[key] = False
                result = result[:idx] + choice + result[end_idx+1:]
                i = idx + len(choice)
            else:
                i = end_idx + 1

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

    active_plural = {}
    token_idx = 0
    while token_idx < len(tokens):
        token = tokens[token_idx]
        if token["type"] != "text":
            token_idx += 1
            continue
            
        val = token["value"]
        idx = val.find("{")
        if idx == -1:
            token_idx += 1
            continue
            
        end_idx = val.find("}", idx)
        if end_idx == -1:
            token_idx += 1
            continue
            
        tag = val[idx+1:end_idx]
        left_text = val[:idx]
        right_text = val[end_idx+1:]
        
        if "?" in tag:
            parts = tag.split("?")
            key = parts[0]
            options = parts[1].split("|")

            base_key, plural_only, add_coll = _resolve_key(key)

            if base_key in TERMS:
                pool = [e for e in TERMS[base_key] if not plural_only or (isinstance(e, tuple) and e[1] == "plural")]
                choice = choose_unique(rng, pool or TERMS[base_key], used_terms)
                raw_choice = choice[0] if isinstance(choice, (list, tuple)) else choice
                if isinstance(choice, (list, tuple)):
                    itype = choice[1]
                    choice = format_item("", choice, rng, add_collective=add_coll)
                    is_plural = (itype == "plural" and not choice.lower().startswith(("a ", "an ")))
                else:
                    choice = format_item("", choice, rng, add_collective=add_coll)
                    is_plural = False

                active_plural[base_key] = is_plural
                active_plural[base_key + "_COLLECTIVE"] = is_plural

                suffix = options[0] if is_plural else options[1] if len(options) > 1 else options[0]
                if suffix and suffix[0].isalnum():
                    suffix_val = " " + suffix
                else:
                    suffix_val = suffix

                new_tokens = []
                if left_text:
                    new_tokens.append({"type": "text", "value": left_text})
                new_tokens.append({
                    "type": "term",
                    "key": base_key,
                    "value": choice,
                    "raw_value": raw_choice,
                    "adj": "",
                    "add_collective": add_coll
                })
                new_tokens.append({"type": "text", "value": suffix_val + right_text})

                tokens[token_idx:token_idx+1] = new_tokens
            elif key in ("MAP_LOCATION", "VILLAGE", "DESTINATION"):
                values = MAP_LOCATIONS if key == "MAP_LOCATION" else VILLAGES if key == "VILLAGE" else (MAP_LOCATIONS + VILLAGES)
                choice = choose_unique(rng, values, used_terms)
                if key == "VILLAGE" or (key == "DESTINATION" and choice in VILLAGES):
                    full_text_before = "".join(t["value"] for t in tokens[:token_idx]) + left_text
                    context_before = full_text_before[max(0, len(full_text_before) - 20):]
                    choice = format_village(choice, context_before)

                is_plural = False
                active_plural[key] = is_plural

                suffix = options[0] if is_plural else options[1] if len(options) > 1 else options[0]
                if suffix and suffix[0].isalnum():
                    suffix_val = " " + suffix
                else:
                    suffix_val = suffix

                new_tokens = []
                if left_text:
                    new_tokens.append({"type": "text", "value": left_text})
                new_tokens.append({
                    "type": "term",
                    "key": key,
                    "value": choice,
                    "raw_value": choice,
                    "adj": ""
                })
                new_tokens.append({"type": "text", "value": suffix_val + right_text})

                tokens[token_idx:token_idx+1] = new_tokens
            else:
                is_plural = active_plural.get(key, False)
                verb = options[0] if is_plural else options[1] if len(options) > 1 else options[0]
                token["value"] = left_text + verb + right_text
        else:
            # Standard placeholder
            key = tag
            base_key, plural_only, add_coll = _resolve_key(key)

            if base_key in TERMS:
                pool = [e for e in TERMS[base_key] if not plural_only or (isinstance(e, tuple) and e[1] == "plural")]
                choice = choose_unique(rng, pool or TERMS[base_key], used_terms)
                raw_choice = choice[0] if isinstance(choice, (list, tuple)) else choice
                if isinstance(choice, (list, tuple)):
                    itype = choice[1]
                    choice = format_item("", choice, rng, add_collective=add_coll)
                    is_plural = (itype == "plural" and not choice.lower().startswith(("a ", "an ")))
                else:
                    choice = format_item("", choice, rng, add_collective=add_coll)
                    is_plural = False

                active_plural[base_key] = is_plural
                active_plural[base_key + "_COLLECTIVE"] = is_plural

                new_tokens = []
                if left_text:
                    new_tokens.append({"type": "text", "value": left_text})
                new_tokens.append({
                    "type": "term",
                    "key": base_key,
                    "value": choice,
                    "raw_value": raw_choice,
                    "adj": "",
                    "add_collective": add_coll
                })
                if right_text:
                    new_tokens.append({"type": "text", "value": right_text})

                tokens[token_idx:token_idx+1] = new_tokens
            elif key in ("MAP_LOCATION", "VILLAGE", "DESTINATION"):
                values = MAP_LOCATIONS if key == "MAP_LOCATION" else VILLAGES if key == "VILLAGE" else (MAP_LOCATIONS + VILLAGES)
                choice = choose_unique(rng, values, used_terms)
                if key == "VILLAGE" or (key == "DESTINATION" and choice in VILLAGES):
                    full_text_before = "".join(t["value"] for t in tokens[:token_idx]) + left_text
                    context_before = full_text_before[max(0, len(full_text_before) - 20):]
                    choice = format_village(choice, context_before)
                    
                active_plural[key] = False
                
                new_tokens = []
                if left_text:
                    new_tokens.append({"type": "text", "value": left_text})
                new_tokens.append({
                    "type": "term",
                    "key": key,
                    "value": choice,
                    "raw_value": choice,
                    "adj": ""
                })
                if right_text:
                    new_tokens.append({"type": "text", "value": right_text})
                    
                tokens[token_idx:token_idx+1] = new_tokens
            else:
                token_idx += 1

    if tokens and tokens[0]["value"]:
        val = tokens[0]["value"]
        tokens[0]["value"] = val[0].upper() + val[1:]
        
    vowels = "aeiouAEIOU"
    
    def get_next_word(start_idx):
        for j in range(start_idx, len(tokens)):
            val = tokens[j]["value"]
            words = val.split()
            if words:
                return words[0].lstrip("`\"'(")
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
                                next_w = parts[k].lstrip("`\"'(")
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
