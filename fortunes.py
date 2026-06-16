# Fortune Teller Template Generation Module
# 
# Total Unique Combinations Formula:
# Sum_{template in TEMPLATES} ( Product_{placeholder in template} len(TERMS[placeholder]) )
# 
# Current counts:
# - SUBJECT (S) = 15
# - VERB (V) = 17
# - OBJECT (O) = 17
# - ACTION (A) = 17
# - MAP_LOCATION (M) = 19
# - VILLAGE (L) = 109
# - DESTINATION (D) = len(MAP_LOCATION) + len(VILLAGE) = 128
# - HAZARD (H) = 15
# - ADJECTIVE (J) = 13
# - ITEM (I) = 15
# - DEVICE (C) = 13
# - TECH_TRIVIA (T) = 13
# - TIME (E) = 12
# - LUCKY_NUMBER (N) = 12
# 
# Template combinations breakdown:
# 1. S * V * O * D      = 15 * 17 * 17 * 128 = 554,880
# 2. S * A * D          = 15 * 17 * 128 = 32,640
# 3. H * A * D          = 15 * 17 * 128 = 32,640
# 4. L * A              = 109 * 17 = 1,853
# 5. J * I * A          = 13 * 15 * 17 = 3,315
# 6. C * V * O * D      = 13 * 17 * 17 * 128 = 480,896
# 7. A * D * C * O      = 17 * 128 * 13 * 17 = 480,896
# 8. S * A * D          = 15 * 17 * 128 = 32,640
# 9. A * J * I          = 17 * 13 * 15 = 3,315
# 10. A * E * J * I * D = 17 * 12 * 13 * 15 * 128 = 5,091,840
# 11. C * H * D         = 13 * 15 * 128 = 24,960
# 12. T * A             = 13 * 17 = 221
# 13. H * A * D         = 15 * 17 * 128 = 32,640
# 14. V * O * D         = 17 * 17 * 128 = 36,992
# 15. S * D * I         = 15 * 128 * 15 = 28,800
# 16. C * O * D         = 13 * 17 * 128 = 28,304
# 17. C * L             = 13 * 109 = 1,417
# 18. E * T * S         = 12 * 13 * 15 = 2,340
# 19. D * T             = 128 * 13 = 1,664
# 20. D * E * S * A     = 128 * 12 * 15 * 17 = 391,680
# 21. S * D * A         = 15 * 128 * 17 = 32,640
# 22. C * E * H         = 13 * 12 * 15 = 2,340
# 23. I * S * D         = 15 * 15 * 128 = 28,800
# 24. L * T             = 109 * 13 = 1,417
# 25. C * J * I * D     = 13 * 13 * 15 * 128 = 324,480
# 26. S * V * C * D     = 15 * 17 * 13 * 128 = 424,320
# 27. E * O * M         = 12 * 17 * 19 = 3,876
# 28. N * J * I         = 12 * 13 * 15 = 2,340
# 29. D * A             = 128 * 17 = 2,176
# 30. H * D * M         = 15 * 128 * 19 = 36,480
# 
# Total Unique Combinations: 8,122,802

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
    "Stage A", "Stage B", "Stage C", "Stage D", "NullSector", "The Robot Arms",
    "accessible camping", "Camping N1", "Camping N2", "Camping N3",
    "Camping C1", "Camping C2", "Camping C3", "Camping S1", "Camping S2",
    "Camping S3 (Quiet)", "the Gate", "the catering zone", "the food queue"
]

VILLAGES = [
    "&nbsp;", ".shhhh", "2016's Worst Village", "3t.network", "All your bass are belong to us",
    "AMSAT-UK", "Astro Observability", "Axov Village", "Bench", "Biohackers",
    "Bodgeham-on-Wye", "Brighton Consulate", "Bristol Hackspace", "brittany (the og one)",
    "Brum and Besties (BABS)", "Cambridge Makespace", "Cardiff Makerspace", "Cheltenham Hackspace",
    "Clockwork Bods", "com:LAAG", "Content Creators Village", "D.I.B.S.", "DogsbodyHQ",
    "Dreamcat & Friends", "Duck Armada", "East Essex Hackspace", "ECHQ", "Edinburgh Hacklab",
    "EMF CTF", "EMF-IX", "ERR_NAME_NOT_RESOLVED", "Field-FX", "Flame village",
    "Forge & Craft / HackWimbledon", "Foundry Zero", "Freeside", "Friends of the Fractal Fern",
    "Friends of the Moon", "Furry High Commission", "GCHQ.NET", "Glasgow Hackerspace",
    "Glastonledburyshire-on-Severn", "Gold member lounge", "Gothic Valley", "Guild of (Bread) Makers",
    "Habville", "Hack Club", "Hackalot", "Hackeriet & Friends", "Hacky Racers",
    "Hardware Hacking Area", "Hat village", "Homebrew, Historical and Retro Computing",
    "Hove, actually", "Håck ma's village", "IGNORE ALL PRIOR VILLAGES", "Irish Embassy",
    "KnobsVille", "Koala Makers", "Leeds Hackspace", "Leigh Hackspace", "LOC",
    "Lock Picking Village", "Loitering Within Tent", "London Aerospace", "Maker Space Newcastle",
    "Maths Village", "meow meow village", "Milliways", "Ministry of Chaos", "MK Makerspace",
    "Model Village", "Moose", "Motley Crew", "NADHack", "Non-Virtual Infraclub",
    "NoobSpace", "Nottingham Hackspace", "Ominous Systems Inc.", "Oxford's EOF Hackspace",
    "Party Pals", "pilk", "Poorly Located Progesterone", "rLab - Reading Hackspace",
    "Scottish Consulate", "SeriousCamp", "Sheffield-by-the-Sea", "Shonkbot",
    "Shonkbot-sur-les-roues", "Shrubbery", "Sibermerdeka", "South London Makerspace",
    "Spark Life (HV Village)", "Stroopwafels & Oatcakes", "Swansea Hackspace",
    "Teesside Hackspace", "Tekhnē-cal Village", "Tented Vias", "Test Village",
    "The Deerdog Domain", "The Hacking Hamlet", "Threadz 'n' Webz", "Traditional Crafts",
    "Tricky Disco", "Unaffiliated Village", "Unnamed Village", "Village of Certain Doom",
    "York Hackspace", "ZTL"
]

TERMS = {
    "SUBJECT": [
        "a new friend", "a rogue robot", "an over-caffeinated volunteer", "a friendly furry",
        "a mysterious hacker", "Jonty", "a space traveler",
        "a volunteer", "a local DJ", "an event organizer", "a cybernetic creature",
        "a retro gamer", "a BGP router whisperer"
    ],
    "VERB": [
        "accidentally delete", "solder", "debug", "trade with", "spill a drink on",
        "explain lockpicking to", "program", "optimize", "repair", "upgrade the firmware of",
        "find", "discover", "reverse engineer", "misplace", "re-solder", "overclock",
        "analyse the packets of"
    ],
    "OBJECT": [
        "some code optimisations", "a custom PCB", "a cold beverage", "an ancient floppy disk",
        "a rogue LED", "a deprecated microchip", "a mysterious GPS rave bot", "a hidden easter egg",
        "a soldering iron", "a BGP router", "a 3D printer", "a Tesla coil", "a pocket-sized synth",
        "some sketchy firmware", "a prototype hexpansion", "a bag of SMD parts", "a dual-beam oscilloscope"
    ],
    "ACTION": [
        "volunteer at the bar", "take a risk", "solve a difficult puzzle", "take a break",
        "start a side project", "sleep for 8 hours", "go on an adventure", "learn lockpicking",
        "explore the campsite network", "solder some SMD components", "attend a talk on retro computing",
        "stay up all night coding", "tinker with high-voltage gear", "exchange rare electronic parts",
        "write firmware in MicroPython", "repair retro arcade games", "configure a custom gateway"
    ],
    "MAP_LOCATION": MAP_LOCATIONS,
    "VILLAGE": VILLAGES,
    "DESTINATION": MAP_LOCATIONS + VILLAGES,
    "HAZARD": [
        "loose solder joints", "unsecured tents", "high powered lasers", "roaming gps rave bots",
        "spiders in the camp", "infinite loops", "poorly crimped cables", "RF interference",
        "memory leaks", "sudden power cuts", "overheated soldering irons", "depleted badge batteries",
        "unlabeled USB sticks", "rogue DHCP servers", "over-caffeinated hackers"
    ],
    "ADJECTIVE": [
        "flashing", "digital", "copper-plated", "glowing", "cybernetic", "clandestine",
        "mysterious", "analog", "overclocked", "deprecated", "quantum-entangled", "ultra-bright",
        "waterproof"
    ],
    "ITEM": [
        "badge addon", "firmware update", "solder joint", "frequency shift", "duck",
        "cup of tea", "USB drive", "LED strip", "crimp tool", "oscilloscope", "component bag",
        "soldering flux", "custom PCB", "RF antenna", "jumper wire"
    ],
    "DEVICE": [
        "Tildagon badge", "solder station", "oscilloscope", "BGP router", "3D printer",
        "Tesla coil", "amateur radio", "Wi-Fi antenna", "soldering iron", "portable console",
        "logic analyzer", "SDR dongle", "microcontroller board"
    ],
    "TECH_TRIVIA": [
        "BGP peering", "solder joints", "firmware updates", "memory leaks", "GPIO pins",
        "custom PCBs", "RF frequencies", "hexpansions", "BGP routing tables", "SMD soldering techniques",
        "MicroPython garbage collection", "Fourier transforms", "packet switching protocols"
    ],
    "TIME": [
        "at midnight", "during the opening talk", "before the closing ceremony", "at dawn",
        "during the next power cut", "under the cover of darkness", "while volunteering",
        "after the second beer", "at exactly 0x4141 ticks", "during the daily badge sync",
        "during a heavy downpour", "before the EMF group photo"
    ],
    "LUCKY_NUMBER": [
        "seven", "thirteen", "forty-two", "eighty-eight", "0x4141", "1337", "65535",
        "three", "twenty-six", "0xCAFE", "four hundred and four", "eight thousand and eighty"
    ]
}

TEMPLATES = [
    "{SUBJECT} will {VERB} {OBJECT} at {DESTINATION}.",
    "{SUBJECT} should {ACTION} at {DESTINATION}.",
    "Beware of {HAZARD} when you {ACTION} at {DESTINATION}.",
    "A session at {VILLAGE} will inspire you to {ACTION}.",
    "You will discover a {ADJECTIVE} {ITEM} while trying to {ACTION}.",
    "Your {DEVICE} will {VERB} {OBJECT} at {DESTINATION}.",
    "While trying to {ACTION} at {DESTINATION}, your {DEVICE} will interface with {OBJECT}.",
    "You will meet {SUBJECT} who will help you {ACTION} at {DESTINATION}.",
    "To {ACTION}, you must first find a {ADJECTIVE} {ITEM}.",
    "If you {ACTION} {TIME}, you will find a {ADJECTIVE} {ITEM} at {DESTINATION}.",
    "Your {DEVICE} will detect {HAZARD} near {DESTINATION}.",
    "A talk about {TECH_TRIVIA} will explain how to {ACTION}.",
    "To avoid {HAZARD}, you should {ACTION} at {DESTINATION}.",
    "Your luckiest moment today will be when you {VERB} {OBJECT} at {DESTINATION}.",
    "{SUBJECT} at {DESTINATION} will offer you a {ITEM} in exchange for debugging assistance.",
    "You will accidentally drop your {DEVICE} near {OBJECT} at {DESTINATION}.",
    "Your {DEVICE} will start picking up strange signals from {VILLAGE}.",
    "{TIME}, you will spend time attempting to explain {TECH_TRIVIA} to {SUBJECT}.",
    "A mysterious flashing LED at {DESTINATION} is actually a secret message about {TECH_TRIVIA}.",
    "If you visit {DESTINATION} {TIME}, you will be asked to help {SUBJECT} {ACTION}.",
    "{SUBJECT} at {DESTINATION} will help you {ACTION}.",
    "Your {DEVICE} will fail {TIME} due to {HAZARD}.",
    "To trade a {ITEM} with {SUBJECT}, you should visit {DESTINATION}.",
    "A session at {VILLAGE} will teach you about {TECH_TRIVIA}.",
    "You will accidentally trade your {DEVICE} for a {ADJECTIVE} {ITEM} at {DESTINATION}.",
    "Beware of {SUBJECT} trying to {VERB} your {DEVICE} at {DESTINATION}.",
    "{TIME}, you will find {OBJECT} near {MAP_LOCATION}.",
    "Your luckiest number is {LUCKY_NUMBER} and your luckiest item is a {ADJECTIVE} {ITEM}.",
    "A mysterious signal at {DESTINATION} suggests you should {ACTION}.",
    "If you see {HAZARD} at {DESTINATION}, quickly run to {MAP_LOCATION}."
]

def format_village(name, context_before):
    name_lower = name.lower().strip()
    
    # Proper noun exceptions that don't need prefix/suffix (just quotes)
    proper_noun_exceptions = {
        "milliways", "bodgeham-on-wye", "glastonledburyshire-on-severn", 
        "sheffield-by-the-sea"
    }
    
    if name_lower in proper_noun_exceptions:
        return f'"{name}"'
        
    # Check if name is self-descriptive (contains town/place words)
    self_descriptive_words = [
        "hackspace", "hacklab", "makespace", "makerspace", "make space", "maker space",
        "consulate", "embassy", "village", "sector", "camp", "lounge", "area", "house", 
        "room", "hq", "lab", "division", "station", "centre", "center", "ville"
    ]
    is_self_descriptive = any(word in name_lower for word in self_descriptive_words)
    if is_self_descriptive:
        return f'"{name}"'
        
    # Check suffix words for collective/club nouns
    collective_nouns = [
        "club", "armada", "commission", "society", "project", "team", "group", 
        "network", "force", "consortium", "union", "association", "friends", 
        "bods", "racers", "pals", "gamers", "makers", "biohackers"
    ]
    ends_with_collective = any(name_lower.endswith(noun) for noun in collective_nouns)
    
    if ends_with_collective:
        return f'the "{name}" village'
        
    # Default: prefix with "the village"
    return f'the village "{name}"'

def fix_a_an(text):
    vowels = "aeiouAEIOU"
    words = text.split(" ")
    for i in range(len(words) - 1):
        if words[i].lower() == "a":
            next_word = words[i+1]
            clean_next = next_word.lstrip('`"\'(')
            if clean_next and clean_next[0] in vowels:
                if words[i] == "A":
                    words[i] = "An"
                else:
                    words[i] = "an"
    return " ".join(words)

def generate_fortune(seed_val):
    rng = SeededRandom(seed_val)
    template = rng.choice(TEMPLATES)
    
    result = template
    # Replace all placeholders `{KEY}` dynamically based on TERMS
    for key, values in TERMS.items():
        placeholder = "{" + key + "}"
        while placeholder in result:
            choice = rng.choice(values)
            # If it's a village (or destination that is in VILLAGES), format it!
            if key == "VILLAGE" or (key == "DESTINATION" and choice in VILLAGES):
                idx = result.find(placeholder)
                context_before = result[max(0, idx - 20):idx]
                choice = format_village(choice, context_before)
                
            # Replace only the first occurrence to ensure fresh choice if placeholder appears multiple times
            result = result.replace(placeholder, choice, 1)
            
    if result:
        result = result[0].upper() + result[1:]
        result = fix_a_an(result)
    return result
