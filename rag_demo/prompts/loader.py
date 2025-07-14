import os

class PromptLoader:
    def __init__(self, prompt_dir: str = "prompts"): # before: prompts
        self.prompt_dir = prompt_dir

    def load(self, name: str) -> str:
        """Lädt eine .txt-Datei basierend auf einem Namen."""
        path = os.path.join(self.prompt_dir, f"{name}.txt")
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Prompt-Datei '{path}' nicht gefunden.")
        with open(path, encoding="utf-8") as f:
            return f.read()

    def format(self, name: str, **kwargs) -> str:
        """Lädt und formatiert den Prompt."""
        template = self.load(name)
        return template.format(**kwargs)
