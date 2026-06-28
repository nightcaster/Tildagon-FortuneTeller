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

    def weighted_choice(self, lst):
        if not lst:
            return None
        total_weight = 0.0
        for item, weight in lst:
            total_weight += weight
        if total_weight <= 0:
            return lst[0][0]
        r = (self.next_int() / 2147483647.0) * total_weight
        running = 0.0
        for item, weight in lst:
            running += weight
            if r <= running:
                return item[0] if isinstance(item, (list, tuple)) else item
        return lst[-1][0]

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
        ("friend", "NOUN:countable"),
        ("volunteer", "NOUN:countable"),
        ("furry", "NOUN:countable"),
        ("hacker", "NOUN:countable"),
        ("Null Sector DJ", "NOUN:countable", "Null Sector DJs"),
        ("event organizer", "NOUN:countable"),
    ],
    "CREATURE": [
        ("robot", "NOUN:countable"),
        ("creature", "NOUN:countable"),
        ("duck", "NOUN:countable"),
        ("spider", "NOUN:countable"),
        ("sentient hexpansion", "NOUN:countable", "hexpansions"),
        ("rogue deer", "NOUN:countable", "rogue deer"),
        ("GPS rave bots", "NOUN:plural"),
        ("volunteers", "NOUN:plural"),
    ],
    "COMPUTE_VERB": [
        ("debug", "debugs", "debugging", "debugged"),
        ("program", "programs", "programming", "programmed"),
        ("optimize", "optimizes", "optimizing", "optimized"),
        ("compile", "compiles", "compiling", "compiled"),
        ("hack", "hacks", "hacking", "hacked"),
        ("engineer", "engineers", "engineering", "engineered"),
        ("social engineer", "social engineers", "social engineering", "social engineered"),
        ("reverse engineer", "reverse engineers", "reverse engineering", "reverse engineered"),
        ("analyse", "analyses", "analysing", "analysed"),
    ],
    "HARDWARE_VERB": [
        ("solder", "solders", "soldering", "soldered"),
        ("hack", "hacks", "hacking", "hacked"),
        ("repair", "repairs", "repairing", "repaired"),
        ("upgrade", "upgrades", "upgrading", "upgraded"),
        ("reverse engineer", "reverse engineers", "reverse engineering", "reverse engineered"),
        ("overclock", "overclocks", "overclocking", "overclocked"),
        ("re-solder", "re-solders", "re-soldering", "re-soldered"),
    ],
    "SOCIAL_VERB": [
        ("trade with", "trades with", "trading with", "traded with"),
        ("spill a drink on", "spills a drink on", "spilling a drink on", "spilled a drink on"),
        ("buy a drink for", "buys a drink for", "buying a drink for", "bought a drink for"),
        ("discover", "discovers", "discovering", "discovered"),
        ("find", "finds", "finding", "found"),
        ("misplace", "misplaces", "misplacing", "misplaced"),
        ("dance with", "dances with", "dancing with", "danced with"),
        ("sing kareoke with", "sings kareoke with", "singing karekoke with", "sang kareoke with"),
    ],
    "HACKER_ADVERB": [
        "enthusiastically",
        "frantically",
        "accidentally",
        "mysteriously",
        "quietly",
        "nervously",
        "suspiciously",
        "hastily",
        "reluctantly",
        "unexpectedly",
    ],
    "ACTIVE_DEVICE": [
        ("Tildagon", "NOUN:countable"),
        ("laptop", "NOUN:countable"),
        ("RFID reader", "NOUN:countable"),
        ("Flipper Zero", "NOUN:countable"),
        ("microcontroller", "NOUN:countable"),
        ("smartphone", "NOUN:countable"),
        ("DECT phone", "NOUN:countable"),
    ],
    "BENCH_TOOL": [
        ("solder station", "NOUN:countable"),
        ("oscilloscope", "NOUN:countable"),
        ("3D printer", "NOUN:countable"),
        ("amateur radio", "NOUN:countable"),
        ("SDR receiver", "NOUN:countable"),
        ("soldering iron", "NOUN:countable"),
    ],
    "COMPUTE_TARGET": [
        ("hidden easter egg", "NOUN:countable"),
        ("3.5\" floppy disk", "NOUN:countable"),
        ("arcade machine", "NOUN:countable"),
        ("game cartridge", "NOUN:countable"),
        ("someone else's badges", "NOUN:plural"),
        ("someone else's badge", "NOUN:mass"),
        ("sketchy firmware", "NOUN:mass"),
    ],
    "HARDWARE_TARGET": [
        ("custom PCB", "NOUN:countable", "custom PCBs"),
        ("tiny IC", "NOUN:countable", "tiny ICs"),
        ("GPS tracker", "NOUN:countable"),
        ("prototype hexpansion", "NOUN:countable"),
        ("overpowered microcontroller", "NOUN:countable"),
        ("oscilloscope", "NOUN:countable"),
        ("prototype Tildagon frontboard", "NOUN:countable"),
        ("digital synth", "NOUN:countable"),
        ("unfinished hexpansion", "NOUN:countable"),
    ],
    "SOCIAL_OBJECT": [
        ("cold beverage", "NOUN:countable"),
        ("badge addon", "NOUN:countable"),
        ("duck", "NOUN:countable"),
        ("dynamic token", "NOUN:countable"),
    ],
    "ABSURD_OBJECT": [
        ("duck", "NOUN:countable"),
        ("bratwurst", "NOUN:countable"),
        ("dynamic token", "NOUN:countable"),
        ("LED strip woven into a hammock", "NOUN:countable"),
        ("spider wearing a tiny high-vis vest", "NOUN:countable"),
        ("spiders wearing tiny high-vis vests", "NOUN:plural"),
        ("solder flux", "NOUN:mass", "tube of"),
    ],
    "CAMP_ACTION": [
        ("volunteer at the bar", "volunteers at the bar", "volunteering at the bar", "volunteered at the bar"),
        ("take a break", "takes a break", "taking a break", "took a break"),
        ("go on an adventure", "goes on an adventure", "going on an adventure", "went on an adventure"),
        ("sleep for 8 hours", "sleeps for 8 hours", "sleeping for 8 hours", "slept for 8 hours"),
        ("attend a talk on retro computing", "attends a talk on retro computing", "attending a talk on retro computing", "attended a talk on retro computing"),
        ("stay up all night coding", "stays up all night coding", "staying up all night coding", "stayed up all night coding"),
    ],
    "HACKER_ACTION": [
        ("take a risk", "takes a risk", "taking a risk", "took a risk"),
        ("solve a difficult puzzle", "solves a difficult puzzle", "solving a difficult puzzle", "solved a difficult puzzle"),
        ("start a side project", "starts a side project", "starting a side project", "started a side project"),
        ("learn lockpicking", "learns lockpicking", "learning lockpicking", "learned lockpicking"),
        ("explore the campsite network", "explores the campsite network", "exploring the campsite network", "explored the campsite network"),
        ("solder some SMD components", "solders some SMD components", "soldering some SMD components", "soldered some SMD components"),
        ("tinker with high-voltage gear", "tinkers with high-voltage gear", "tinkering with high-voltage gear", "tinkered with high-voltage gear"),
        ("exchange rare electronic parts", "exchanges rare electronic parts", "exchanging rare electronic parts", "exchanged rare electronic parts"),
        ("write firmware in MicroPython", "writes firmware in MicroPython", "writing firmware in MicroPython", "wrote firmware in MicroPython"),
        ("repair retro arcade games", "repairs retro arcade games", "repairing retro arcade games", "repaired retro arcade games"),
        ("configure a custom gateway", "configures a custom gateway", "configuring a custom gateway", "configured a custom gateway"),
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
        ("badge addon", "NOUN:countable"),
        ("firmware update", "NOUN:countable"),
        ("USB drive", "NOUN:countable"),
        ("LED strip", "NOUN:countable"),
        ("oscilloscope", "NOUN:countable"),
        ("custom PCB", "NOUN:countable"),
        ("RF antenna", "NOUN:countable"),
        ("resistors", "NOUN:plural", "strip of"),
        ("solder", "NOUN:mass", "spool of"),
        ("fiber optic cable", "NOUN:mass", "length of"),
        ("thermal paste", "NOUN:mass", "dollop of"),
    ],
    "CRAFT_ITEM": [
        ("solder joint", "NOUN:countable"),
        ("duck", "NOUN:countable"),
        ("cup of tea", "NOUN:countable"),
        ("crimp tool", "NOUN:countable"),
        ("component bag", "NOUN:countable"),
        ("jumper wire", "NOUN:countable"),
        ("soldering flux", "NOUN:mass", "roll of"),
        ("conductive thread", "NOUN:mass", "bobbin of"),
        ("club mate", "NOUN:mass", "bottle of"),
        ("hot glue", "NOUN:mass", "stick of"),
        ("felt", "NOUN:mass", "sheet of"),
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
        ("a walk around", "walks around", "walking around", "walked around"),
        ("an amble towards", "ambles towards", "ambling towards", "ambled towards"),
        ("a gentle stroll past", "strolls past", "strolling past", "strolled past"),
        ("a quick run around", "runs around", "running around", "ran around"),
        ("a late-night wander near", "wanders near", "wandering near", "wandered near"),
        ("a brief march past", "marches past", "marching past", "marched past"),
        ("a session at", "sessions at", "sessioning at", "sessioned at"),
        ("a visit to", "visits to", "visiting to", "visited to"),
        ("a few drinks at", "drinks at", "drinking at", "drank at"),
    ],
    "CAMPING_ITEM": [
        ("your socks", "NOUN:mass"),
        ("your sleeping bag", "NOUN:mass"),
        ("your airbed", "NOUN:mass"),
        ("your tent", "NOUN:mass"),
        ("your camping chair", "NOUN:mass"),
        ("your backpack", "NOUN:mass"),
    ],
    "CAMPING_LOCATION": [
        ("inside your socks", "NOUN:mass"),
        ("in the depth of your sleeping bag", "NOUN:mass"),
        ("in the bowels of your tent", "NOUN:mass"),
        ("in the queue for the showers", "NOUN:mass"),
        ("in the toilets", "NOUN:mass"),
        ("in the bar", "NOUN:mass"),
        ("in the info tent", "NOUN:mass"),
    ],
    "FESTIVAL_INFRASTRUCTURE": [
        ("stuck telehandler", "NOUN:countable"),
        ("stuck van", "NOUN:countable"),
        ("the DECT phone system", "NOUN:mass"),
        ("the fibre backbone", "NOUN:mass"),
        ("the Wi-Fi infrastructure", "NOUN:mass"),
        ("a soiled Datenklo", "NOUN:mass"),
    ],
}

UPBEAT_TEMPLATES = [
    ('You might see Jonty {TIME} {HARDWARE_VERB_ACTIVE} {FESTIVAL_INFRASTRUCTURE} using {CREATURE_PLURAL_COLLECTIVE}.', 9.055),
    ('{TECH_ADJECTIVE+TECH_ITEM} gives your {ACTIVE_DEVICE} {SPECIAL_DEVICE_FEATURE}.', 10.567),
    ('A mysterious firmware update signed by Kliment grants your Tildagon {SPECIAL_DEVICE_FEATURE}.', 29.43),
    ('A ping on port 8081 {TIME} signals incoming {TECH_ADJECTIVE+CREATURE_PLURAL}', 12.489),
    ('Be on the lookout for {HARDWARE_TARGET} to {HARDWARE_VERB}', 16.127),
    ('Quick! You should be {CAMP_ACTION_ACTIVE}', 28.119),
    ('If you like {HARDWARE_TARGET}, check {CAMPING_LOCATION}.', 16.127),
    ('If {CREATURE} makes eye contact, {HACKER_ACTION}.', 16.023),
    ('If {PEOPLE_SUBJECT?mention|mentions} Jonty, change the topic.', 24.048),
    ('If you see {CREATURE_PLURAL}, offer them {CAMPING_ITEM}.', 19.56),
    ('If you see {PEOPLE_SUBJECT}, compliment their outfit.', 24.048),
    ('If you see {HARDWARE_TARGET}, admire it from afar.', 22.17),
    ('You will find fame and fortune {CAMPING_LOCATION}.', 27.099),
    ('{CREATURE?are|is} not what they seem...', 24.048),
    ('If {PEOPLE_SUBJECT?are coding late|is coding late}, make them some tea!.', 24.048),
]
DEFAULT_TEMPLATES = [
    ('{PEOPLE_SUBJECT} will {HACKER_ADVERB+SOCIAL_VERB} {CREATURE}.', 9.879),
    ('Try {CAMP_ACTION_ACTIVE} at {DESTINATION}.', 12.869),
    ('Your code will finally compile after {VISIT_TYPE} {MAP_LOCATION}.', 15.466),
    ('{CREATURE_PLURAL_COLLECTIVE} riding {CREATURE_PLURAL} will bring great fortune to {VILLAGE}.', 8.873),
    ('{PEOPLE_SUBJECT_COLLECTIVE} will {CAMP_ACTION} .', 12.825),
    ('{VISIT_TYPE} {VILLAGE} will inspire you to {CAMP_ACTION}.', 10.483),
    ('{CREATURE} will {SOCIAL_VERB+PEOPLE_SUBJECT} near {MAP_LOCATION}.', 9.363),
    ('You will discover {CRAFT_ADJECTIVE+CRAFT_ITEM} while trying to {HACKER_ACTION}.', 12.247),
    ('Your {ACTIVE_DEVICE} will flawlessly {COMPUTE_VERB} {COMPUTE_TARGET}.', 13.018),
    ('While trying to {HACKER_ACTION} at {DESTINATION}, {ABSURD_OBJECT} will appear.', 10.149),
    ('You will meet {PEOPLE_SUBJECT_COLLECTIVE} who will help you {HACKER_ACTION}.', 12.014),
    ('To {CAMP_ACTION}, you must first find {TECH_ADJECTIVE+TECH_ITEM}.', 12.608),
    ('To {CAMP_ACTION}, you must first obtain {CRAFT_ADJECTIVE+CRAFT_ITEM}.', 13.091),
    ('If you {CAMP_ACTION} {TIME}, you might find {TECH_ADJECTIVE+TECH_ITEM}.', 9.911),
    ('If you {CAMP_ACTION} {TIME}, you might create {CRAFT_ADJECTIVE+CRAFT_ITEM}.', 10.207),
    ('A talk about {TECH_TRIVIA} will explain how to easily {HACKER_ACTION}.', 16.023),
    ('You will find luck when you {COMPUTE_VERB} {COMPUTE_TARGET}.', 16.691),
    ('Fortune awaits when you {HARDWARE_VERB} {HARDWARE_TARGET}.', 16.127),
    ('{PEOPLE_SUBJECT} at {DESTINATION} will offer you {TECH_SHINY_ITEM} in exchange for debugging assistance.', 9.564),
    ('Your {BENCH_TOOL} will work better near {VILLAGE}.', 13.104),
    ('If you visit {DESTINATION} {TIME}, you might get to {CAMP_ACTION}.', 10.071),
    ('{PEOPLE_SUBJECT} at {DESTINATION} will help you {HACKER_ACTION}.', 9.564),
    ('To trade {TECH_RARE_ITEM} with {PEOPLE_SUBJECT}, you should visit {DESTINATION}.', 9.564),
    ('A session at {VILLAGE} will teach you all about {TECH_TRIVIA}.', 12.146),
    ('Your luckiest number is {LUCKY_NUMBER} and your luckiest item is {TECH_ADJECTIVE+TECH_ITEM}.', 11.719),
    ('Your luckiest number is {LUCKY_NUMBER} and your luckiest item is {CRAFT_ADJECTIVE+CRAFT_ITEM}.', 12.134),
    ('A mysterious friendly signal at {DESTINATION} suggests you should immediately {CAMP_ACTION}.', 12.869),
]
OMINOUS_TEMPLATES = [
    ('Beware of {HAZARD} when you {CAMP_ACTION}.', 16.925),
    ('You will meet a new nemesis while trying to {HACKER_ACTION} at the {MAP_LOCATION}.', 15.06),
    ('Beware of {CREATURE_PLURAL} bearing {SOCIAL_OBJECT}.', 21.007),
    ('Beware of {CREATURE_PLURAL} near {DESTINATION}.', 12.869),
    ('Your {ACTIVE_DEVICE} will detect high levels of {HAZARD} near {DESTINATION}.', 9.75),
    ('To avoid {HAZARD}, you should quickly {CAMP_ACTION}.', 16.925),
    ('You will accidentally drop your beloved {ACTIVE_DEVICE}. Butter fingers.', 27.099),
    ('{TIME}, you will spend hours attempting to explain {TECH_TRIVIA} to {CREATURE}.', 11.799),
    ('A mysterious flashing LED at {DESTINATION} is actually an ominous message about {TECH_TRIVIA}.', 11.943),
    ('Your {ACTIVE_DEVICE} will fail due to {HAZARD}.', 16.55),
    ('You will accidentally trade your {ACTIVE_DEVICE} for {TECH_ADJECTIVE+TECH_ITEM}.', 12.399),
    ('You will accidentally trade your {ACTIVE_DEVICE} for {CRAFT_ADJECTIVE+CRAFT_ITEM}.', 12.865),
    ('Beware of {CREATURE} trying to {COMPUTE_VERB} your unprotected {ACTIVE_DEVICE}.', 12.892),
    ('Beware of {CREATURE} trying to {HARDWARE_VERB} your unguarded {ACTIVE_DEVICE}.', 13.265),
    ('If you see {HAZARD} creeping around {DESTINATION}, take shelter at {MAP_LOCATION}.', 8.989),
    ('If you see Jonty sprinting toward {DESTINATION}, do not ask questions. Do not follow him.', 16.092),
    ('Jonty will challenge you to a game of chance behind {MAP_LOCATION}.', 21.942),
    ('Beware of {HAZARD} when compiling code for {ACTIVE_DEVICE}.', 16.55),
    ('{PEOPLE_SUBJECT} will {CAMP_ACTION} despite being advised not to.', 17.499),
    ('Your {ACTIVE_DEVICE} will slowly begin to resent you for not {CAMP_ACTION_ACTIVE}', 19.06),
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
            clean_next = words[i+1].lstrip("`\\\"'(")
            if clean_next and clean_next[0] in vowels:
                first_word = clean_next.lower().strip(".,;:!?\"'()")
                if not first_word.startswith("usb"):
                    words[i] = "An" if words[i] == "A" else "an"
    return " ".join(words)

def remove_possessive_articles(text):
    possessives = {"your", "my", "his", "her", "its", "our", "their"}
    words = text.split(" ")
    i = 0
    while i < len(words):
        word_lower = words[i].lower()
        if word_lower in ("a", "an"):
            preceded = False
            if i - 1 >= 0:
                prev_1 = words[i-1].lower().strip(".,;:!?\"'()")
                if prev_1 in possessives:
                    preceded = True
                elif i - 2 >= 0:
                    prev_2 = words[i-2].lower().strip(".,;:!?\"'()")
                    if prev_2 in possessives:
                        preceded = True
            if preceded:
                words.pop(i)
                continue
        i += 1
    return " ".join(words)

def clean_possessive_articles_tokens(tokens):
    possessives = {"your", "my", "his", "her", "its", "our", "their"}
    for i in range(len(tokens)):
        token = tokens[i]
        if token["type"] == "text":
            token["value"] = remove_possessive_articles(token["value"])
        elif token["type"] == "term":
            val = token["value"]
            val_lower = val.lower()
            prefix_len = 0
            if val_lower.startswith("a "):
                prefix_len = 2
            elif val_lower.startswith("an "):
                prefix_len = 3
                
            if prefix_len > 0:
                preceding_text = "".join(t["value"] for t in tokens[:i])
                words = preceding_text.split()
                preceded = False
                if len(words) >= 1:
                    prev_1 = words[-1].lower().strip(".,;:!?\"'()")
                    if prev_1 in possessives:
                        preceded = True
                    elif len(words) >= 2:
                        prev_2 = words[-2].lower().strip(".,;:!?\"'()")
                        if prev_2 in possessives:
                            preceded = True
                if preceded:
                    token["value"] = val[prefix_len:]

COLLECTIVE_PREFIXES = [
    "herd of",
    "gaggle of",
    "conference of",
    "swarm of",
    "parade of",
    "tsunami of",
    "mob of",
    "cabal of",
    "flock of",
    "some"
]

def pluralize(noun):
    if not noun:
        return ""
    words = noun.split(" ")
    word = words[-1]
    lower_word = word.lower()
    
    if lower_word.endswith("y"):
        if len(lower_word) > 1 and lower_word[-2] not in "aeiou":
            plural_word = word[:-1] + "ies"
        else:
            plural_word = word + "s"
    elif lower_word.endswith(("s", "x", "z", "ch", "sh")):
        plural_word = word + "es"
    elif lower_word.endswith("fe"):
        plural_word = word[:-2] + "ves"
    elif lower_word.endswith("f") and not lower_word.endswith("ff"):
        plural_word = word[:-1] + "ves"
    else:
        plural_word = word + "s"
        
    words[-1] = plural_word
    return " ".join(words)

def format_item(adjective, item, rng=None, add_collective=False, force_plural=False):
    if isinstance(item, (list, tuple)):
        name = item[0]
        itype = item[1]
        unit = None
        is_collective = False
        if itype == "NOUN:countable" and add_collective and rng:
            if (rng.next_int() >> 8) % 2 == 0:
                unit = rng.choice(COLLECTIVE_PREFIXES)
                is_collective = True
        elif itype == "NOUN:plural" and add_collective and rng:
            if (rng.next_int() >> 8) % 2 == 0:
                unit = rng.choice(COLLECTIVE_PREFIXES)
                is_collective = True
                
        if itype == "NOUN:plural" and not add_collective:
            unit = item[2] if len(item) > 2 else None

        if force_plural or is_collective or itype == "NOUN:plural":
            if itype == "NOUN:countable":
                if len(item) > 2 and item[2]:
                    name = item[2]
                else:
                    name = pluralize(name)
                itype = "NOUN:plural"
        else:
            unit = None
    else:
        name = item
        itype = "NOUN:countable"
        if force_plural:
            name = pluralize(name)
            itype = "NOUN:plural"
        unit = None

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
        if itype == "NOUN:countable":
            return fix_a_an(f"a {phrase}")
        return phrase

def _resolve_key(key):
    '''
    Strip _PLURAL, _COLLECTIVE, _ACTIVE, and/or _PAST suffixes from a template placeholder key.
    Returns (base_key, plural_only, add_collective, active_only, past_only).
    '''
    add_collective = False
    plural_only = False
    active_only = False
    past_only = False
    if key.endswith("_COLLECTIVE"):
        key = key[:-len("_COLLECTIVE")]
        add_collective = True
    if key.endswith("_PLURAL"):
        key = key[:-len("_PLURAL")]
        plural_only = True
    if key.endswith("_ACTIVE"):
        key = key[:-len("_ACTIVE")]
        active_only = True
    if key.endswith("_PAST"):
        key = key[:-len("_PAST")]
        past_only = True
    return key, plural_only, add_collective, active_only, past_only

def is_preceded_by_modal(text, index):
    preceding = text[:index].rstrip()
    if not preceding:
        return False
    words = preceding.split()
    if not words:
        return False
    last_word = words[-1].lower().strip(".,;:!?\"'()")
    return last_word in {"will", "would", "shall", "should", "can", "could", "may", "might", "must", "to"}

# Noun-type markers recognised in TERMS tuple entries
_NOUN_TYPES = ("NOUN:countable", "NOUN:plural", "NOUN:mass")

def _resolve_chain(chain_key, rng, used_terms, active_plural, force_infinitive=False):
    parts = chain_key.split("+")
    output_parts = []
    subject_is_plural = None
    pending_adjective = None

    for part in parts:
        base_key, plural_only, add_coll, active_only, past_only = _resolve_key(part)

        if base_key not in TERMS:
            continue

        pool = TERMS[base_key]
        if plural_only:
            filtered = [e for e in pool if not isinstance(e, tuple) or e[1] in ("NOUN:countable", "NOUN:plural")]
            if filtered:
                pool = filtered

        choice = choose_unique(rng, pool or TERMS[base_key], used_terms)

        if isinstance(choice, tuple) and choice[1] in _NOUN_TYPES:
            # Noun — format with article / collective prefix, apply pending adjective
            adj = pending_adjective or ""
            formatted = format_item(adj, choice, rng, add_collective=add_coll, force_plural=plural_only)
            is_pl = (choice[1] == "NOUN:plural" or plural_only) and not formatted.lower().startswith(("a ", "an "))
            if subject_is_plural is None:
                subject_is_plural = is_pl
                active_plural[base_key] = is_pl
                active_plural[base_key + "_COLLECTIVE"] = is_pl
            
            if pending_adjective is not None and len(output_parts) > 0 and output_parts[-1] == pending_adjective:
                output_parts[-1] = formatted
            else:
                output_parts.append(formatted)
            pending_adjective = None
        elif isinstance(choice, tuple):
            # Verb pair — pick form based on subject plurality or active_plural fallback
            if active_only:
                val = choice[2] if len(choice) > 2 else choice[0]
            elif past_only:
                val = choice[3] if len(choice) > 3 else choice[0]
            elif force_infinitive:
                val = choice[0]
            elif subject_is_plural is not None:
                val = choice[0] if subject_is_plural else choice[1]
            elif active_plural:
                val = choice[0] if list(active_plural.values())[-1] else choice[1]
            else:
                val = choice[0]
            output_parts.append(val)
            pending_adjective = None
        else:
            # Plain string (adverb / adjective) — use as-is
            output_parts.append(choice)
            pending_adjective = choice

    is_plural = subject_is_plural if subject_is_plural is not None else (list(active_plural.values())[-1] if active_plural else True)
    return " ".join(output_parts), is_plural

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
        template = rng.weighted_choice(UPBEAT_TEMPLATES)
    else:
        template = rng.weighted_choice(OMINOUS_TEMPLATES)
        
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

            if "+" in key:
                # Chain with conditional suffix: e.g. "{PEOPLE_SUBJECT+SOCIAL_VERB?themselves|themself}"
                force_inf = is_preceded_by_modal(result, idx)
                choice, is_plural = _resolve_chain(key, rng, used_terms, active_plural, force_infinitive=force_inf)
            else:
                base_key, plural_only, add_coll, active_only, past_only = _resolve_key(key)

                if base_key in TERMS:
                    pool = TERMS[base_key]
                    if plural_only:
                        filtered = [e for e in pool if not isinstance(e, tuple) or e[1] in ("NOUN:countable", "NOUN:plural")]
                        if filtered:
                            pool = filtered
                    choice = choose_unique(rng, pool or TERMS[base_key], used_terms)
                    if isinstance(choice, tuple) and choice[1] in _NOUN_TYPES:
                        itype = choice[1]
                        choice = format_item("", choice, rng, add_collective=add_coll, force_plural=plural_only)
                        is_plural = (itype == "NOUN:plural" or plural_only) and not choice.lower().startswith(("a ", "an "))
                    elif isinstance(choice, tuple):
                        if active_only:
                            choice = choice[2] if len(choice) > 2 else choice[0]
                        elif past_only:
                            choice = choice[3] if len(choice) > 3 else choice[0]
                        else:
                            force_inf = is_preceded_by_modal(result, idx)
                            if force_inf:
                                choice = choice[0]
                            elif active_plural:
                                choice = choice[0] if list(active_plural.values())[-1] else choice[1]
                            else:
                                choice = choice[0]
                        is_plural = False
                    else:
                        is_plural = False  # plain string: use as-is

                    active_plural[base_key] = is_plural
                    active_plural[base_key + "_COLLECTIVE"] = is_plural
                elif key in ("MAP_LOCATION", "VILLAGE", "DESTINATION"):
                    values = MAP_LOCATIONS if key == "MAP_LOCATION" else VILLAGES if key == "VILLAGE" else (MAP_LOCATIONS + VILLAGES)
                    choice = choose_unique(rng, values, used_terms)
                    if key == "VILLAGE" or (key == "DESTINATION" and choice in VILLAGES):
                        context_before = result[max(0, idx - 20):idx]
                        choice = format_village(choice, context_before)
                    is_plural = False
                    active_plural[key] = is_plural
                else:
                    # Reference to a previously resolved key's plurality
                    is_plural = active_plural.get(key, False)
                    verb = options[0] if is_plural else options[1] if len(options) > 1 else options[0]
                    result = result[:idx] + verb + result[end_idx+1:]
                    i = idx + len(verb)
                    continue

            suffix = options[0] if is_plural else options[1] if len(options) > 1 else options[0]
            if suffix and suffix[0].isalnum():
                val = choice + " " + suffix
            else:
                val = choice + suffix
            result = result[:idx] + val + result[end_idx+1:]
            i = idx + len(val)
        else:
            # Standard placeholder
            key = tag

            if "+" in key:
                # Chain: e.g. "{PEOPLE_SUBJECT+HACKER_ADVERB+SOCIAL_VERB}"
                force_inf = is_preceded_by_modal(result, idx)
                choice, is_plural = _resolve_chain(key, rng, used_terms, active_plural, force_infinitive=force_inf)
                result = result[:idx] + choice + result[end_idx+1:]
                i = idx + len(choice)
            else:
                base_key, plural_only, add_coll, active_only, past_only = _resolve_key(key)

                if base_key in TERMS:
                    pool = TERMS[base_key]
                    if plural_only:
                        filtered = [e for e in pool if not isinstance(e, tuple) or e[1] in ("NOUN:countable", "NOUN:plural")]
                        if filtered:
                            pool = filtered
                    choice = choose_unique(rng, pool or TERMS[base_key], used_terms)
                    if isinstance(choice, tuple) and choice[1] in _NOUN_TYPES:
                        itype = choice[1]
                        choice = format_item("", choice, rng, add_collective=add_coll, force_plural=plural_only)
                        is_plural = (itype == "NOUN:plural" or plural_only) and not choice.lower().startswith(("a ", "an "))
                    elif isinstance(choice, tuple):
                        if active_only:
                            choice = choice[2] if len(choice) > 2 else choice[0]
                        elif past_only:
                            choice = choice[3] if len(choice) > 3 else choice[0]
                        else:
                            force_inf = is_preceded_by_modal(result, idx)
                            if force_inf:
                                choice = choice[0]
                            elif active_plural:
                                choice = choice[0] if list(active_plural.values())[-1] else choice[1]
                            else:
                                choice = choice[0]
                        is_plural = False
                    else:
                        is_plural = False  # plain string: use as-is

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
        result = remove_possessive_articles(result)
    return result

def is_token_preceded_by_modal(tokens, token_idx, left_text=""):
    preceding_text = ""
    for k in range(token_idx):
        preceding_text += tokens[k]["value"]
    preceding_text += left_text
    return is_preceded_by_modal(preceding_text, len(preceding_text))

def generate_fortune_metadata(seed_val):
    rng = SeededRandom(seed_val)
    
    vibe_roll = rng.next_int() % 100
    if vibe_roll < 85:
        template = rng.weighted_choice(UPBEAT_TEMPLATES)
        vibe = "upbeat"
    else:
        template = rng.weighted_choice(OMINOUS_TEMPLATES)
        vibe = "ominous"
        
    tokens = [{"type": "text", "value": template}]
    used_terms = set()
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

            if "+" in key:
                choice, is_plural = _resolve_chain(key, rng, used_terms, active_plural)
                raw_choice = choice
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
                    "raw_value": raw_choice,
                    "adj": "",
                    "add_collective": False
                })
                new_tokens.append({"type": "text", "value": suffix_val + right_text})
                tokens[token_idx:token_idx+1] = new_tokens
            else:
                base_key, plural_only, add_coll, active_only, past_only = _resolve_key(key)

                if base_key in TERMS:
                    pool = TERMS[base_key]
                    if plural_only:
                        filtered = [e for e in pool if not isinstance(e, tuple) or e[1] in ("NOUN:countable", "NOUN:plural")]
                        if filtered:
                            pool = filtered
                    choice = choose_unique(rng, pool or TERMS[base_key], used_terms)
                    raw_choice = choice[0] if isinstance(choice, (list, tuple)) else choice
                    if isinstance(choice, tuple) and choice[1] in _NOUN_TYPES:
                        itype = choice[1]
                        choice = format_item("", choice, rng, add_collective=add_coll, force_plural=plural_only)
                        is_plural = (itype == "NOUN:plural" or plural_only) and not choice.lower().startswith(("a ", "an "))
                    elif isinstance(choice, tuple):
                        raw_choice = choice[0]
                        if active_only:
                            choice = choice[2] if len(choice) > 2 else choice[0]
                        elif past_only:
                            choice = choice[3] if len(choice) > 3 else choice[0]
                        else:
                            force_inf = is_token_preceded_by_modal(tokens, token_idx, left_text)
                            if force_inf:
                                choice = choice[0]
                            elif active_plural:
                                choice = choice[0] if list(active_plural.values())[-1] else choice[1]
                            else:
                                choice = choice[0]
                        is_plural = False
                    else:
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

            if "+" in key:
                choice, is_plural = _resolve_chain(key, rng, used_terms, active_plural)
                new_tokens = []
                if left_text:
                    new_tokens.append({"type": "text", "value": left_text})
                new_tokens.append({
                    "type": "term",
                    "key": key,
                    "value": choice,
                    "raw_value": choice,
                    "adj": "",
                    "add_collective": False
                })
                if right_text:
                    new_tokens.append({"type": "text", "value": right_text})
                tokens[token_idx:token_idx+1] = new_tokens
            else:
                base_key, plural_only, add_coll, active_only, past_only = _resolve_key(key)

                if base_key in TERMS:
                    pool = TERMS[base_key]
                    if plural_only:
                        filtered = [e for e in pool if not isinstance(e, tuple) or e[1] in ("NOUN:countable", "NOUN:plural")]
                        if filtered:
                            pool = filtered
                    choice = choose_unique(rng, pool or TERMS[base_key], used_terms)
                    raw_choice = choice[0] if isinstance(choice, (list, tuple)) else choice
                    if isinstance(choice, tuple) and choice[1] in _NOUN_TYPES:
                        itype = choice[1]
                        choice = format_item("", choice, rng, add_collective=add_coll, force_plural=plural_only)
                        is_plural = (itype == "NOUN:plural" or plural_only) and not choice.lower().startswith(("a ", "an "))
                    elif isinstance(choice, tuple):
                        raw_choice = choice[0]
                        if active_only:
                            choice = choice[2] if len(choice) > 2 else choice[0]
                        elif past_only:
                            choice = choice[3] if len(choice) > 3 else choice[0]
                        else:
                            force_inf = is_token_preceded_by_modal(tokens, token_idx, left_text)
                            if force_inf:
                                choice = choice[0]
                            elif active_plural:
                                choice = choice[0] if list(active_plural.values())[-1] else choice[1]
                            else:
                                choice = choice[0]
                        is_plural = False
                    else:
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
                        
                    if next_w and next_w[0] in vowels and not next_w.lower().startswith("usb"):
                        parts[p_idx] = "An" if word == "A" else "an"
                        changed = True
            if changed:
                token["value"] = " ".join(parts)

    clean_possessive_articles_tokens(tokens)
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
