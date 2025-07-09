from .base import DocProcessor

class FallbackProcessor(DocProcessor):
    def extract_text(self) -> str:
        # Einfach nur Hinweistext zurückgeben oder leeren String
        return f"[Keine Verarbeitung definiert für Datei: {self.file_path}]"

    def get_type(self) -> str:
        return "Unbekannter Dokumenttyp"
