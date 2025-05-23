import random

def generate_postcard(sight, weather):
    templates = [
        f"Today I visited {sight.name}, a lovely {sight.category} in Paris. The weather was {weather}, perfect for it!",
        f"Strolling through Paris, I stopped by {sight.name}. It's especially beautiful when it's {weather}.",
        f"{sight.name} was the highlight of my {weather} day — such charm and peace."
    ]
    return random.choice(templates)