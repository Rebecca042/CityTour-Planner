from .base import DocProcessor

class TagebuchProcessor(DocProcessor):
    def extract_text(self) -> str:
        # Angenommen, Tagebuch ist einfache TXT-Datei
        with open(self.file_path, "r", encoding="utf-8") as f:
            return f.read()

    def get_type(self) -> str:
        return "Tagebuch"
