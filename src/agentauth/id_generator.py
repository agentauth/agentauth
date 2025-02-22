import random

# Lists of adjectives and animals for ID generation
ADJECTIVES = [
    "happy", "clever", "swift", "bright", "gentle", "brave", "calm", "wise",
    "quick", "kind", "bold", "smart", "eager", "fair", "keen", "nice", 
    "proud", "warm", "cool", "sharp", "agile", "witty", "merry", "lively",
    "noble", "sunny", "jolly", "spry", "fresh", "alert", "grand", "crisp",
    "sweet", "pure", "prime", "clear", "light", "safe", "sure", "free",
    "firm", "good", "true", "fine", "real", "fast", "rich", "neat", 
    "soft", "deft", "wild", "zesty", "vital", "ready", "plucky", "perky",
    "lucid", "loyal", "magic", "daring", "blithe", "apt", "adept", "brisk",
    "civil", "elite", "exact", "fancy", "fleet", "frank", "game", "hardy",
    "ideal", "mild", "nimble", "rapid", "sage", "sleek", "stark", "super",
    "tidy", "trim", "trusty", "urban", "valid", "young", "ace", "active",
    "acute", "arch", "astute", "balanced", "basic", "bonny", "breezy",
    "bubbly", "cheery", "chief", "choice", "cosmic"
]

ANIMALS = [
    "panda", "tiger", "eagle", "dolphin", "wolf", "fox", "owl", "bear",
    "lion", "deer", "hawk", "seal", "cat", "dog", "bird", "fish",
    "koala", "whale", "rabbit", "elephant", "giraffe", "penguin",
    "kangaroo", "octopus", "cheetah", "gorilla", "rhino", "hippo", "monkey",
    "jaguar", "leopard", "lynx", "raccoon", "otter", "beaver", "badger",
    "hedgehog", "squirrel", "chipmunk", "hamster", "mouse", "rat", "mole",
    "bat", "sloth", "armadillo", "anteater", "camel", "llama", "alpaca",
    "sheep", "goat", "cow", "pig", "horse", "donkey", "mule", "zebra",
    "antelope", "gazelle", "moose", "elk", "bison", "buffalo", "crocodile",
    "alligator", "turtle", "tortoise", "snake", "lizard", "iguana", "gecko",
    "chameleon", "frog", "toad", "salamander", "newt", "shark", "stingray",
    "jellyfish", "starfish", "crab", "lobster", "shrimp", "clam", "oyster",
    "snail", "slug", "butterfly", "moth", "bee", "wasp", "ant", "spider",
    "scorpion", "centipede", "millipede", "worm", "parrot", "macaw", "toucan",
    "peacock", "ostrich", "emu", "duck", "goose", "swan", "crane", "stork"
]

def generate_id() -> str:
    """
    Generate a random ID in the format {adjective}-{animal}-{number}
    
    Returns:
        str: A randomly generated ID
    """
    adjective = random.choice(ADJECTIVES)
    animal = random.choice(ANIMALS)
    number = random.randint(100000, 999999)
    
    return f"{adjective}-{animal}-{number}" 
